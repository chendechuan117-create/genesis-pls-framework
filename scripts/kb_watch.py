#!/usr/bin/env python3
"""
KB 实时观测脚本 — 监控 Genesis 知识库变化
用法:
  python3 scripts/kb_watch.py              # 默认 10s 轮询
  python3 scripts/kb_watch.py --interval 5  # 5s 轮询
  python3 scripts/kb_watch.py --once        # 只拍一次快照
"""

import sqlite3
import time
import argparse
import os
import sys
from datetime import datetime

DB_PATH = os.path.expanduser("~/.genesis/workshop_v4.sqlite")

NTYPE_ICON = {
    "LESSON":  "📖",
    "ASSET":   "🧰",
    "CONTEXT": "🔵",
    "EPISODE": "🎬",
    "ENTITY":  "🏷️",
    "TOOL":    "⚙️",
    "EVENT":   "⚡",
    "ACTION":  "🦾",
}


def get_snapshot(conn):
    cur = conn.execute("""
        SELECT node_id, ntype, title, confidence_score, usage_count,
               usage_success_count, usage_fail_count, updated_at
        FROM knowledge_nodes
        WHERE node_id NOT LIKE 'MEM_CONV%'
        ORDER BY updated_at DESC
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return {r[0]: dict(zip(cols, r)) for r in rows}


def get_summary(conn):
    cur = conn.execute("""
        SELECT ntype, COUNT(*) as cnt,
               ROUND(AVG(confidence_score), 3) as avg_conf,
               SUM(usage_count) as total_usage,
               SUM(usage_success_count) as wins,
               SUM(usage_fail_count) as losses
        FROM knowledge_nodes
        WHERE node_id NOT LIKE 'MEM_CONV%'
        GROUP BY ntype ORDER BY cnt DESC
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


def get_recent_nodes(conn, n=10):
    cur = conn.execute("""
        SELECT node_id, ntype, title, confidence_score, updated_at
        FROM knowledge_nodes
        WHERE node_id NOT LIKE 'MEM_CONV%'
        ORDER BY updated_at DESC LIMIT ?
    """, (n,))
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


def get_arena_stats(conn):
    cur = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(usage_success_count) as wins,
               SUM(usage_fail_count) as losses,
               COUNT(CASE WHEN confidence_score < 0.4 THEN 1 END) as low_conf,
               COUNT(CASE WHEN usage_count = 0 THEN 1 END) as never_used
        FROM knowledge_nodes
        WHERE node_id NOT LIKE 'MEM_CONV%'
    """)
    r = cur.fetchone()
    return dict(zip([d[0] for d in cur.description], r))


def print_summary(conn, label=""):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'═'*60}")
    print(f"  KB 快照 {ts}  {label}")
    print(f"{'═'*60}")

    rows = get_summary(conn)
    total = sum(r["cnt"] for r in rows)
    print(f"{'类型':<10} {'数量':>5} {'平均信心':>8} {'使用':>6} {'W/L':>10}")
    print(f"{'─'*50}")
    for r in rows:
        icon = NTYPE_ICON.get(r["ntype"], "❓")
        wl = f"{r['wins'] or 0}W/{r['losses'] or 0}L"
        print(f"{icon} {r['ntype']:<8} {r['cnt']:>5} {r['avg_conf']:>8.3f} {r['total_usage']:>6} {wl:>10}")
    print(f"{'─'*50}")

    arena = get_arena_stats(conn)
    win_rate = arena["wins"] / (arena["wins"] + arena["losses"]) if (arena["wins"] or 0) + (arena["losses"] or 0) > 0 else 0
    print(f"总计: {total} 节点 | Arena {win_rate*100:.1f}% 胜率 | {arena['low_conf']} 低信心 | {arena['never_used']} 从未使用")

    print(f"\n🕐 最近更新 (Top 8):")
    for r in get_recent_nodes(conn, 8):
        icon = NTYPE_ICON.get(r["ntype"], "❓")
        conf = r["confidence_score"] or 0
        bar = "█" * int(conf * 10) + "░" * (10 - int(conf * 10))
        ts_short = (r["updated_at"] or "")[:16]
        title = r["title"][:40] if r["title"] else r["node_id"]
        print(f"  {icon} [{conf:.2f}] {bar} {ts_short}  {title}")


def diff_snapshots(old, new):
    """返回 (new_nodes, changed_nodes, deleted_nodes)"""
    old_ids = set(old.keys())
    new_ids = set(new.keys())

    added = [new[nid] for nid in new_ids - old_ids]
    deleted = [old[nid] for nid in old_ids - new_ids]
    changed = []
    for nid in old_ids & new_ids:
        o, n = old[nid], new[nid]
        if (o["confidence_score"] != n["confidence_score"]
                or o["usage_count"] != n["usage_count"]
                or o["title"] != n["title"]):
            changed.append({"old": o, "new": n})

    return added, changed, deleted


def print_diff(added, changed, deleted):
    if not (added or changed or deleted):
        print(f"  (无变化)")
        return

    for n in sorted(added, key=lambda x: x["ntype"]):
        icon = NTYPE_ICON.get(n["ntype"], "❓")
        conf = n["confidence_score"] or 0
        print(f"  ✨ NEW  {icon} [{conf:.2f}] {n['ntype']:<8} {(n['title'] or n['node_id'])[:55]}")

    for c in changed:
        o, n = c["old"], c["new"]
        icon = NTYPE_ICON.get(n["ntype"], "❓")
        conf_old = o["confidence_score"] or 0
        conf_new = n["confidence_score"] or 0
        delta_conf = conf_new - conf_old
        delta_use = (n["usage_count"] or 0) - (o["usage_count"] or 0)
        parts = []
        if abs(delta_conf) > 0.001:
            arrow = "↑" if delta_conf > 0 else "↓"
            parts.append(f"conf {conf_old:.2f}→{conf_new:.2f}({arrow}{abs(delta_conf):.3f})")
        if delta_use:
            parts.append(f"usage+{delta_use}")
        if parts:
            print(f"  🔄 CHG  {icon} {(n['title'] or n['node_id'])[:45]}  {', '.join(parts)}")

    for n in deleted:
        print(f"  🗑️  DEL  {(n['title'] or n['node_id'])[:55]}")


def main():
    parser = argparse.ArgumentParser(description="Genesis KB 实时观测")
    parser.add_argument("--interval", type=int, default=10, help="轮询间隔(秒)")
    parser.add_argument("--once", action="store_true", help="只拍一次快照后退出")
    parser.add_argument("--db", default=DB_PATH, help="SQLite 路径")
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"Error: DB 不存在: {args.db}")
        sys.exit(1)

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, check_same_thread=False)

    print_summary(conn, "(初始快照)")
    if args.once:
        conn.close()
        return

    old_snap = get_snapshot(conn)
    print(f"\n👁️  开始监控，每 {args.interval}s 轮询一次。Ctrl+C 退出。\n")

    try:
        while True:
            time.sleep(args.interval)
            conn2 = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, check_same_thread=False)
            new_snap = get_snapshot(conn2)
            added, changed, deleted = diff_snapshots(old_snap, new_snap)

            ts = datetime.now().strftime("%H:%M:%S")
            if added or changed or deleted:
                print(f"\n[{ts}] ▶ 检测到变化 (+{len(added)} new, ~{len(changed)} chg, -{len(deleted)} del):")
                print_diff(added, changed, deleted)
            else:
                sys.stdout.write(f"\r[{ts}] 无变化")
                sys.stdout.flush()

            old_snap = new_snap
            conn2.close()

    except KeyboardInterrupt:
        print("\n\n监控结束。")
        print_summary(conn, "(最终快照)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
