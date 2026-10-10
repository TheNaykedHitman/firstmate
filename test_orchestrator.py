#!/usr/bin/env python3
"""
Test script for the Firstmate Windows Orchestrator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from firstmate_orchestrator import main
from firstmate_orchestrator.orca_bridge import OrcaBridge


def test_orca_bridge():
    print('Testing OrcaBridge...')
    bridge = OrcaBridge()
    print(f"Worktree creation: {'SUCCESS' if bridge.create_worktree('test-worktree', 'main') else 'FAILED'}")
    print(f"Agent binding: {'SUCCESS' if bridge.bind_agent('test-worktree', 'claude-code') else 'FAILED'}")
    print(f"Task dispatch: {'SUCCESS' if bridge.dispatch_task('test-worktree', 'Refactor this component') else 'FAILED'}")
    scripts = bridge.list_shell_scripts(Path('../Git Repositories Cloned/firstmate/bin'))
    print(f'Found {len(scripts)} shell scripts in firstmate bin directory')


if __name__ == '__main__':
    print('Firstmate Windows Orchestrator - Test Suite')
    print('=' * 45)
    main()
    test_orca_bridge()
    print('\nTests completed.')
