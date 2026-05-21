import asyncio
import inspect
import json
import sys
from datetime import datetime

sys.path.insert(0, '/workspace')

from genesis.core.registry import ToolRegistry
from genesis.tools.node_tools import RecordLessonNodeTool, RecordContextNodeTool, CreateMetaNodeTool, SearchKnowledgeNodesTool
from genesis.v4.loop import GenesisLoop

PAYLOAD = {
    "node_id": "LESSON_PROBE_AUDIT_20260328_B",
    "title": "probe lesson for contract audit",
    "trigger_verb": "audit",
    "trigger_noun": "record_lesson_node",
    "trigger_context": "doctor_minimal_replay",
    "resolves": "probe only",
    "action_steps": ["step1", "step2"],
    "because_reason": "verify current registry/execute contract alignment",
    "prerequisites": [],
    "confidence_score": 0.01,
    "verification_source": "doctor_probe",
    "metadata_signature": {
        "task_kind": "audit",
        "target_kind": "tool",
        "environment_scope": "doctor_sandbox",
        "validation_status": "probe"
    }
}

async def main():
    print('PROBE_T0', datetime.now().isoformat(sep=' ', timespec='seconds'))
    reg = ToolRegistry()
    reg.register(SearchKnowledgeNodesTool())
    reg.register(RecordContextNodeTool())
    reg.register(RecordLessonNodeTool())
    reg.register(CreateMetaNodeTool())
    tool = reg.get('record_lesson_node')
    print('TOOL_CLASS', tool.__class__.__name__)
    print('TOOL_MODULE', tool.__class__.__module__)
    print('TOOL_FILE', inspect.getsourcefile(tool.__class__))
    print('TOOL_NAME', tool.name)
    print('PARAMS_TOP_TYPE', tool.parameters.get('type'))
    print('PARAMS_REQUIRED', tool.parameters.get('required'))
    print('PARAMS_PROPERTIES', sorted(tool.parameters.get('properties', {}).keys()))
    print('EXEC_SIGNATURE', inspect.signature(tool.execute))
    print('REGISTRY_OBJ_TYPE', type(reg.get('record_lesson_node')))
    defs = reg.get_definitions()
    match = next((d for d in defs if d.get('function', {}).get('name') == 'record_lesson_node'), None)
    print('PROVIDER_SCHEMA_FOUND', bool(match))
    if match:
        p = match['function'].get('parameters', {})
        print('PROVIDER_SCHEMA_REQUIRED', p.get('required'))
        print('PROVIDER_SCHEMA_PROPERTIES', sorted(p.get('properties', {}).keys()))

    for label, payload in [
        ('case_a_none', None),
        ('case_b_empty_dict', {}),
        ('case_c_probe_only', {'node_id': 'LESSON_PROBE_ONLY'}),
        ('case_d_full_payload', PAYLOAD),
    ]:
        try:
            result = await reg.execute('record_lesson_node', payload)
            print(f'RESULT {label} {result!r}')
        except Exception as e:
            print(f'EXC {label} {type(e).__name__}: {e}')

    loop = GenesisLoop(reg, provider=None)
    prep = getattr(loop, '_prepare_c_tool_args', None)
    print('HAS_PREPARE_C_TOOL_ARGS', prep is not None)
    if prep:
        for label, payload in [('dict_payload', PAYLOAD), ('json_payload', json.dumps(PAYLOAD, ensure_ascii=False))]:
            try:
                out = prep('record_lesson_node', payload)
                print(f'PREP {label} {out!r}')
            except Exception as e:
                print(f'PREP_EXC {label} {type(e).__name__}: {e}')

asyncio.run(main())
