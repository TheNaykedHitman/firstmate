"""
Windows Environment Abstraction Module
=====================================

This module provides cross-platform path handling and Git integration
for running firstmate on Windows using pathlib.Path and Orca's Git tracking.

Based on analysis of hardcoded Unix paths and Git commands in the firstmate repository.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Union, Optional


class WindowsPathAbstraction:
    """Cross-platform path abstraction for Windows compatibility."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize the path abstraction.
        
        Args:
            base_path: Base path for operations (defaults to current directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
    def get_temp_dir(self) -> Path:
        """Get platform-appropriate temporary directory."""
        return Path(os.environ.get('TEMP', '/tmp'))
        
    def get_user_home(self) -> Path:
        """Get user home directory."""
        return Path.home()
        
    def get_firstmate_config_dir(self) -> Path:
        """Get firstmate configuration directory."""
        # Use APPDATA on Windows, ~/.config elsewhere
        if os.name == 'nt':  # Windows
            config_root = Path(os.environ.get('APPDATA', self.get_user_home() / 'AppData' / 'Roaming'))
        else:  # Unix-like
            config_root = self.get_user_home() / '.config'
            
        return config_root / 'firstmate'
        
    def normalize_path(self, path: Union[str, Path]) -> Path:
        """Normalize a path for the current platform."""
        return Path(path).resolve()
        
    def join_paths(self, *parts) -> Path:
        """Join path parts using platform-appropriate separator."""
        return Path(*parts)
        
    def ensure_directory_exists(self, path: Union[str, Path]) -> bool:
        """
        Ensure a directory exists.
        
        Args:
            path: Path to ensure exists
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False


class GitIntegration:
    """Git integration using Orca's native Git tracking capabilities."""
    
    def __init__(self, repo_path: Union[str, Path]):
        """
        Initialize Git integration.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path)
        
    def run_git_command(self, args: list, json_output: bool = True) -> dict:
        """
        Run a Git command via Orca CLI.
        
        Args:
            args: Git command arguments
            json_output: Whether to request JSON output
            
        Returns:
            Command result as dictionary
        """
        cmd = ["orca"] + args
        if json_output and "--json" not in args:
            cmd.append("--json")
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.repo_path),
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONError:
                    return {"output": result.stdout, "error": "JSON parsing failed"}
            else:
                return {"error": f"Command failed with exit code {result.returncode}", "stderr": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}
            
    def get_repo_status(self) -> dict:
        """Get repository status."""
        return self.run_git_command(["repo", "status"])
        
    def create_worktree(self, name: str, branch: Optional[str] = None) -> dict:
        """Create a Git worktree."""
        args = ["worktree", "create", "--name", name]
        if branch:
            args.extend(["--base-branch", branch])
        return self.run_git_command(args)
        
    def remove_worktree(self, name: str) -> dict:
        """Remove a Git worktree."""
        return self.run_git_command(["worktree", "remove", name])
        
    def list_worktrees(self) -> dict:
        """List Git worktrees."""
        return self.run_git_command(["worktree", "list"])
        
    def get_current_branch(self) -> dict:
        """Get current Git branch."""
        return self.run_git_command(["git", "branch", "--show-current"])
        
    def commit_changes(self, message: str, add_all: bool = True) -> dict:
        """Commit changes to the repository."""
        if add_all:
            self.run_git_command(["git", "add", "."])
        return self.run_git_command(["git", "commit", "-m", message])
        
    def push_changes(self, remote: str = "origin", branch: Optional[str] = None) -> dict:
        """Push changes to remote repository."""
        args = ["git", "push", remote]
        if branch:
            args.append(branch)
        return self.run_git_command(args)


# Utility functions for backwards compatibility
def replace_unix_paths_with_pathlib(code_content: str) -> str:
    """
    Replace hardcoded Unix paths with pathlib.Path equivalents.
    
    Args:
        code_content: String content containing Unix paths
        
    Returns:
        Updated code content with pathlib.Path usage
    """
    import re
    
    # Replace /tmp references
    code_content = re.sub(r'/tmp/([^"\'\s]*)', r'str(Path(get_temp_dir(), "\1"))', code_content)
    
    # Replace $HOME references
    code_content = re.sub(r'\$HOME/([^"\'\s]*)', r'str(Path.home() / "\1")', code_content)
    
    # Replace /var/log references
    code_content = re.sub(r'/var/log/([^"\'\s]*)', r'str(Path("/var/log", "\1"))', code_content)
    
    return code_content


def convert_shell_script_to_python(script_path: Union[str, Path]) -> str:
    """
    Convert a shell script to Python equivalent using Orca CLI.
    
    Args:
        script_path: Path to shell script
        
    Returns:
        Python code equivalent
    """
    script_path = Path(script_path)
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script {script_path} not found")
        
    # Read the shell script
    with open(script_path, 'r') as f:
        content = f.read()
        
    # Simple conversion - this would need to be expanded for full implementation
    python_code = f"# Converted from {script_path.name}\n\n"
    python_code += "import subprocess\nfrom pathlib import Path\n\n"
    python_code += "def main():\n"
    python_code += "    # TODO: Implement shell script logic using Orca CLI\n"
    python_code += "    pass\n\n"
    python_code += "if __name__ == '__main__':\n"
    python_code += "    main()\n"
    
    return python_code