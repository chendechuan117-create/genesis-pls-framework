import importlib.util
from pathlib import Path


def _load_module():
    probe_path = Path(__file__).resolve().parents[1] / 'runtime' / 'scratch' / 'doctor_test_governance_boundary_audit.py'
    spec = importlib.util.spec_from_file_location('doctor_test_governance_boundary_audit', probe_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_governance_boundary_audit_finds_migratable_scratch_db_contract_tests():
    mod = _load_module()
    result = mod.run_audit()

    assert result['doctor_test_count'] >= 10
    assert result['family_counts'].get('scratch_coupled', 0) >= 1
    assert result['family_counts'].get('db_contract', 0) >= 1
    assert result['migration_candidate_count'] >= 1
    assert 'test_doctor_mcp_content_consumer_probe.py' in result['migration_candidate_names']
    assert 'test_doctor_real_non_lesson_content_consumer_probe.py' in result['migration_candidate_names']
