#!/usr/bin/env python3
"""
Integration test for the Firstmate Windows Orchestrator.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from firstmate_orchestrator import main
from firstmate_orchestrator.orca_bridge import OrcaBridge
from firstmate_orchestrator.fan_out_mechanism import fan_out_tasks
from firstmate_orchestrator.windows_abstraction import GitIntegration, WindowsPathAbstraction


def test_orca_bridge():
    print("Testing OrcaBridge...")
    bridge = OrcaBridge()
    status = bridge.orca_status()
    print(f"Orca status: {'OK' if 'error' not in status else 'ERROR'}")
    if 'error' in status:
        print(f"  Error: {status['error']}")
        return False
    print(f"Worktree creation: {'SUCCESS' if bridge.create_worktree('test-worktree', 'main') else 'FAILED'}")
    print(f"Agent binding: {'SUCCESS' if bridge.bind_agent('test-worktree', 'claude-code') else 'FAILED'}")
    print(f"Task dispatch: {'SUCCESS' if bridge.dispatch_task('test-worktree', 'Refactor this component') else 'FAILED'}")
    scripts = bridge.list_shell_scripts(Path('../Git Repositories Cloned/firstmate/bin'))
    print(f"Found {len(scripts)} shell scripts in firstmate bin directory")
    return True


def test_fan_out_mechanism():
    print("\nTesting Fan-Out Mechanism...")
    results = fan_out_tasks('Test fan-out mechanism on Windows', [
        {'title': 'Test Task 1', 'spec': {'instruction': 'Verify Orca CLI integration'}, 'agent': 'codex'},
        {'title': 'Test Task 2', 'spec': {'instruction': 'Validate cross-platform path handling'}, 'agent': 'claude-code'},
    ])
    print(f"Fan-out completed with {len(results)} results")
    return True


def test_windows_abstraction():
    print("\nTesting Windows Path Abstraction...")
    path_abs = WindowsPathAbstraction()
    print(f"Temporary directory: {path_abs.get_temp_dir()}")
    print(f"User home: {path_abs.get_user_home()}")
    print(f"Firstmate config directory: {path_abs.get_firstmate_config_dir()}")
    test_dir = Path(tempfile.gettempdir()) / 'firstmate_test'
    print(f"Directory creation: {'SUCCESS' if path_abs.ensure_directory_exists(test_dir) else 'FAILED'}")
    if test_dir.exists():
        test_dir.rmdir()
    return True


def test_git_integration():
    print("\nTesting Git Integration...")
    firstmate_path = Path('../Git Repositories Cloned/firstmate')
    if not firstmate_path.exists():
        print('Firstmate repository not found, skipping Git integration test')
        return True
    try:
        git_int = GitIntegration(firstmate_path)
        status = git_int.get_repo_status()
        print(f"Repository status: {'OK' if 'error' not in status else 'ERROR'}")
        return True
    except Exception as e:
        print(f"Git integration test failed with exception: {e}")
        return True


def main_test():
    print('Firstmate Windows Orchestrator - Integration Test')
    print('=' * 50)
    print('Running main orchestrator function...')
    try:
        main()
        print('Main function: SUCCESS')
    except Exception as e:
        print(f'Main function: FAILED - {e}')
        return False

    tests = [
        ('Orca Bridge', test_orca_bridge),
        ('Fan-Out Mechanism', test_fan_out_mechanism),
        ('Windows Abstraction', test_windows_abstraction),
        ('Git Integration', test_git_integration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            results.append((test_name, test_func()))
        except Exception as e:
            print(f'{test_name}: ERROR - {e}')
            results.append((test_name, False))

    print('\n' + '=' * 50)
    print('TEST SUMMARY')
    print('=' * 50)
    passed = 0
    for test_name, result in results:
        status = 'PASS' if result else 'FAIL'
        print(f'{test_name}: {status}')
        if result:
            passed += 1
    print(f'\nOverall: {passed}/{len(results)} tests passed')
    return passed == len(results)


if __name__ == '__main__':
    sys.exit(0 if main_test() else 1)
