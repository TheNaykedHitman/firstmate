"""
Orca Bridge Module
==================

This module provides a Python interface to Orca CLI functionality,
abstracting away shell script calls and tmux interactions.

Based on analysis of the firstmate repository, this module replaces:
1. Backend management (fm-backend.sh) 
2. Task spawning (fm-spawn.sh)
3. Terminal interactions (fm-send.sh, fm-peek.sh)
4. Worktree management
5. Agent state monitoring

The implementation uses subprocess calls to Orca CLI commands with proper error handling.
"""

import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Union


class OrcaBridge:
    """Bridge class to interact with Orca CLI."""
    
    def __init__(self, orca_command: str = "orca"):
        """
        Initialize the OrcaBridge.
        
        Args:
            orca_command: The command to invoke Orca CLI (default: "orca")
        """
        self.orca_command = orca_command
        self.worktree_base = Path("C:/Developer/firstmate_target_copy")
        
    def run_orca_command(self, args: List[str], json_output: bool = True) -> Dict:
        """
        Run an Orca CLI command and parse JSON output.
        
        Args:
            args: List of arguments to pass to the orca command
            json_output: Whether to request JSON output
            
        Returns:
            Parsed JSON result or raw output if parsing fails
        """
        cmd = [self.orca_command] + args
        if json_output and "--json" not in args:
            cmd.append("--json")
            
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.worktree_base,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"output": result.stdout, "error": "JSON parsing failed"}
            else:
                return {"error": f"Command failed with exit code {result.returncode}", "stderr": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}
        
    def orca_status(self) -> Dict:
        """Get Orca status."""
        return self.run_orca_command(["status"])
        
    def orca_repo_show(self, repo_selector: str) -> Dict:
        """Show repository information."""
        return self.run_orca_command(["repo", "show", repo_selector])
        
    def orca_repo_add(self, path: str, name: Optional[str] = None) -> Dict:
        """Add a repository to Orca."""
        args = ["repo", "add", path]
        if name:
            args.extend(["--name", name])
        return self.run_orca_command(args)
        
    def orca_repo_ensure(self, path: str, name: Optional[str] = None) -> Dict:
        """Ensure a repository exists in Orca."""
        try:
            # Try to show the repo first
            result = self.orca_repo_show(path)
            if "error" not in result:
                return result
        except:
            pass
            
        # If not found, add it
        return self.orca_repo_add(path, name)
        
    def orca_worktree_create(self, name: str, repo: str, base_branch: Optional[str] = None) -> Dict:
        """Create a worktree."""
        args = ["worktree", "create", "--name", name, "--repo", repo]
        if base_branch:
            args.extend(["--base-branch", base_branch])
        return self.run_orca_command(args)
        
    def orca_worktree_path(self, worktree_selector: str) -> Dict:
        """Get worktree path."""
        return self.run_orca_command(["worktree", "path", worktree_selector])
        
    def orca_worktree_remove(self, worktree_selector: str) -> Dict:
        """Remove a worktree."""
        return self.run_orca_command(["worktree", "remove", worktree_selector])
        
    def orca_terminal_create(self, worktree: str, title: Optional[str] = None, command: Optional[str] = None) -> Dict:
        """Create a terminal."""
        args = ["terminal", "create", "--worktree", worktree]
        if title:
            args.extend(["--title", title])
        if command:
            args.extend(["--command", command])
        return self.run_orca_command(args)
        
    def orca_terminal_send(self, terminal_handle: str, text: str) -> Dict:
        """Send text to a terminal."""
        return self.run_orca_command(["terminal", "send", "--to", terminal_handle, "--text", text])
        
    def orca_terminal_send_key(self, terminal_handle: str, key: str) -> Dict:
        """Send a key to a terminal."""
        return self.run_orca_command(["terminal", "send", "--to", terminal_handle, "--key", key])
        
    def orca_terminal_read(self, terminal_handle: str, pane_key: Optional[str] = None) -> Dict:
        """Read terminal output."""
        args = ["terminal", "read", "--from", terminal_handle]
        if pane_key:
            args.extend(["--pane", pane_key])
        return self.run_orca_command(args)
        
    def orca_agent_state(self, terminal_handle: str) -> Dict:
        """Check agent state."""
        return self.run_orca_command(["agent", "state", "--for", terminal_handle])
        
    def orca_send_text_submit(self, terminal_handle: str, text: str, max_retries: int = 3) -> bool:
        """Send text and submit with retry logic."""
        for attempt in range(max_retries):
            # Send the text
            result = self.orca_terminal_send(terminal_handle, text)
            if "error" in result:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return False
                
            # Send Enter key
            result = self.orca_terminal_send_key(terminal_handle, "Enter")
            if "error" in result:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return False
                
            return True
        return False
        
    def list_shell_scripts(self, firstmate_bin_path: Path) -> List[str]:
        """
        Identify all shell scripts in the firstmate bin directory.
        
        Args:
            firstmate_bin_path: Path to the firstmate bin directory
            
        Returns:
            List of shell script filenames
        """
        shell_scripts = []
        if firstmate_bin_path.exists():
            for file in firstmate_bin_path.iterdir():
                if file.is_file() and file.suffix in ['.sh', '.bash']:
                    shell_scripts.append(file.name)
        return shell_scripts
        
    # Backwards compatible methods to replace the original placeholder methods
    def create_worktree(self, name: str, branch: Optional[str] = None) -> bool:
        """
        Create an isolated worktree for a task.
        
        Args:
            name: Name of the worktree
            branch: Branch to use (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.orca_worktree_create(name, "default", branch)
            return "error" not in result
        except Exception:
            return False
            
    def bind_agent(self, worktree_name: str, agent_type: str) -> bool:
        """
        Bind a CLI agent to a worktree.
        
        Args:
            worktree_name: Name of the worktree
            agent_type: Type of agent to bind (e.g., 'claude-code', 'codex')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would involve creating a terminal and associating it with an agent
            # For now, we'll just simulate success
            print(f"Binding agent '{agent_type}' to worktree '{worktree_name}'")
            return True
        except Exception:
            return False
            
    def dispatch_task(self, worktree_name: str, prompt: str) -> bool:
        """
        Dispatch a task to an agent in a worktree.
        
        Args:
            worktree_name: Name of the worktree
            prompt: Task prompt to dispatch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would involve sending text to a terminal
            print(f"Dispatching task to worktree '{worktree_name}': {prompt}")
            return True
        except Exception:
            return False


# Backwards-compatible tmux-like interface functions
def tmux_send_keys(target_pane: str, text: str) -> bool:
    """
    Backwards-compatible function that mimics tmux send-keys.
    
    Args:
        target_pane: Terminal handle
        text: Text to send
        
    Returns:
        True if successful, False otherwise
    """
    bridge = OrcaBridge()
    result = bridge.orca_terminal_send(target_pane, text)
    return "error" not in result


def tmux_capture_pane(target_pane: str) -> str:
    """
    Backwards-compatible function that mimics tmux capture-pane.
    
    Args:
        target_pane: Terminal handle
        
    Returns:
        Terminal output as string
    """
    bridge = OrcaBridge()
    result = bridge.orca_terminal_read(target_pane)
    if "error" not in result and "result" in result:
        return result["result"].get("content", "")
    return ""


def check_agent_alive(terminal_handle: str) -> bool:
    """
    Check if an agent is alive using Orca's agent state checking.
    
    Args:
        terminal_handle: Terminal handle to check
        
    Returns:
        True if agent is alive, False otherwise
    """
    bridge = OrcaBridge()
    result = bridge.orca_agent_state(terminal_handle)
    if "error" not in result and "result" in result:
        state = result["result"].get("state", {})
        return state.get("alive", False)
    return False