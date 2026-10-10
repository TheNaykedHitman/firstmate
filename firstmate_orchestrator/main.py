"""Main entry point for the Firstmate Windows orchestrator."""

from pathlib import Path


def main() -> None:
    print('Firstmate Windows Orchestrator')
    print('===============================')

    orchestrator_dir = Path('C:/Developer/firstmate_orchestrator')
    target_dir = Path('C:/Developer/firstmate_target_copy')

    print(f'Orchestrator directory: {orchestrator_dir}')
    print(f'Target directory: {target_dir}')

    orchestrator_dir.mkdir(parents=True, exist_ok=True)
    target_dir.mkdir(parents=True, exist_ok=True)

    print('Directories initialized.')


if __name__ == '__main__':
    main()
