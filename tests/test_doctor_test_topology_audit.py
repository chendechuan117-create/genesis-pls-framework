import importlib.util
from pathlib import Path


def _load_module():
    probe_path = Path(__file__).resolve().parents[1] / 'runtime' / 'scratch' / 'doctor_test_topology_audit.py'
    spec = importlib.util.spec_from_file_location('doctor_test_topology_audit', probe_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_doctor_test_topology_splits_self_contained_tests_into_two_stable_families():
    mod = _load_module()
    result = mod.run_audit()

    assert result['doctor_test_count'] >= 10
    assert result['self_contained_count'] >= 1
    assert result['pure_python_count'] >= 1
    assert result['genesis_bound_count'] >= 1
    assert result['db_contract_count'] >= 1
    assert 'test_doctor_rln_envelope_boundary.py' in result['genesis_bound_names']
    assert 'test_doctor_auto_mode_home_snapshot_contract.py' in result['db_contract_names']
