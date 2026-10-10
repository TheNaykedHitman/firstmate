#!/usr/bin/env python3
"""
Python-based fan-out mechanism using Orca CLI commands to create isolated 
worktrees and dispatch tasks to different agent instances.
"""

import json
import subprocess
import sys
from typing import List, Dict, Any


def run_orca_command(args: List[str], json_output: bool = True) -> Dict:
    """
    Run an Orca CLI command and parse JSON output.
    
    Args:
        args: List of arguments to pass to the orca command
        json_output: Whether to request JSON output
        
    Returns:
        Parsed JSON result or raw output if parsing fails
    """
    cmd = ["orca"] + args
    if json_output and "--json" not in args:
        cmd.append("--json")
        
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
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


def create_orchestration_run(objective: str) -> Dict[str, Any]:
    """
    Create and bind a lightweight orchestration Run.
    
    Args:
        objective: The objective for the orchestration run
        
    Returns:
        Dictionary containing the run creation result
    """
    result = run_orca_command(["orchestration", "run-create", "--objective", objective])
    return result


def create_orchestration_task(spec: Dict[str, Any], task_title: str, run_id: str) -> Dict[str, Any]:
    """
    Create an orchestration task.
    
    Args:
        spec: Task specification dictionary
        task_title: Title for the task
        run_id: ID of the run to associate with
        
    Returns:
        Dictionary containing the task creation result
    """
    # Convert spec to JSON string
    spec_json = json.dumps(spec)
    
    args = [
        "orchestration", "task-create",
        "--spec", spec_json,
        "--task-title", task_title,
        "--run", run_id
    ]
    
    result = run_orca_command(args)
    return result


def start_worker(task_id: str, agent: str, worktree_type: str = "new-top-level") -> Dict[str, Any]:
    """
    Start a supervised worker.
    
    Args:
        task_id: ID of the task to start worker for
        agent: Agent to use (e.g., 'codex', 'claude-code')
        worktree_type: Type of worktree to create
        
    Returns:
        Dictionary containing the worker start result
    """
    args = [
        "orchestration", "worker-start",
        "--task", task_id,
        "--agent", agent,
        "--worktree", worktree_type
    ]
    
    result = run_orca_command(args)
    return result


def fan_out_tasks(objective: str, task_specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fan out tasks using Orca CLI commands.
    
    Args:
        objective: Overall objective for the task set
        task_specs: List of task specifications
        
    Returns:
        List of results for each task
    """
    # Create orchestration run
    run_result = create_orchestration_run(objective)
    
    # Extract run_id from the result
    if "error" in run_result:
        return [{"error": "Failed to create run", "details": run_result}]
    
    run_data = run_result.get("result", {})
    run_id = run_data.get("run", {}).get("id")
    
    if not run_id:
        return [{"error": "Could not extract run ID", "details": run_result}]
    
    results = []
    
    # Create and start workers for each task
    for i, spec in enumerate(task_specs):
        task_title = spec.get("title", f"Task {i+1}")
        
        # Create task
        task_result = create_orchestration_task(spec["spec"], task_title, run_id)
        
        if "error" in task_result:
            results.append({
                "error": "Failed to create task",
                "task_spec": spec,
                "details": task_result
            })
            continue
            
        # Extract task ID
        task_data = task_result.get("result", {})
        task_id = task_data.get("task", {}).get("id")
        
        if not task_id:
            results.append({
                "error": "Could not extract task ID",
                "task_spec": spec,
                "details": task_result
            })
            continue
            
        # Start worker
        worker_result = start_worker(
            task_id, 
            spec.get("agent", "codex"),
            spec.get("worktree", "new-top-level")
        )
        
        results.append({
            "task_id": task_id,
            "task_spec": spec,
            "worker_result": worker_result
        })
    
    return results


# Example usage
if __name__ == "__main__":
    # Define the overall objective
    objective = "Refactor firstmate repository for Windows compatibility"
    
    # Define individual task specifications
    tasks = [
        {
            "title": "Research Task 1",
            "spec": {
                "instruction": "Research the latest developments in quantum computing and summarize key findings"
            },
            "agent": "codex",
            "repo": "id:default",
            "base_branch": "main"
        },
        {
            "title": "Development Task 1", 
            "spec": {
                "instruction": "Implement a new feature for the user authentication system"
            },
            "agent": "claude-code",
            "repo": "id:default",
            "base_branch": "develop"
        },
        {
            "title": "Documentation Task 1",
            "spec": {
                "instruction": "Update the API documentation with new endpoints"
            },
            "agent": "cursor",
            "repo": "id:default", 
            "base_branch": "docs"
        }
    ]
    
    # Execute fan-out
    results = fan_out_tasks(objective, tasks)
    
    # Print results
    for result in results:
        print(json.dumps(result, indent=2))