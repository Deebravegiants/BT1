# [M] PraisonAI: Coarse-Grained Tool Approval Cache Bypasses Per-Invocation Consent for Shell Commands

## Summary
Severity: Medium
Advisory: GHSA-ffp3-3562-8cv3
CVE: CVE-2026-56074
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-ffp3-3562-8cv3
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <4.5.128

## Details
## Summary

The approval system in PraisonAI Agents caches tool approval decisions by tool name only, not by invocation arguments. Once a user approves `execute_command` for any command (e.g., `ls -la`), all subsequent `execute_command` calls in that execution context bypass the approval prompt entirely. Combined with `os.environ.copy()` passing all process environment variables to subprocesses, this allows an LLM agent (potentially via prompt injection) to silently exfiltrate API keys and credentials without further user consent.

## Details

The `require_approval` decorator in `src/praisonai-agents/praisonaiagents/approval/__init__.py:176-178` checks approval status by tool name only:

```python
@wraps(func)
def wrapper(*args, **kwargs):
    if is_already_approved(tool_name):   # line 177 — checks only tool_name
        return func(*args, **kwargs)     # line 178 — bypasses ALL approval
```

The `mark_approved` function in `registry.py:144-147` stores only the tool name string:

```python
def mark_approved(self, tool_name: str) -> None:
    approved = self._approved_context.get(set())
    approved.add(tool_name)              # stores "execute_command", not args
    self._approved_context.set(approved)
```

The approval context is never cleared during agent execution — `clear_approved()` exists (`registry.py:152`) but is never called in the agent's tool execution path (`agent/tool_execution.py`).

Meanwhile, the `ConsoleBackend` UI at `backends.py:95-96` misleads the user:

```python
return Confirm.ask(
    f"Do you want to execute this {request.risk_level} risk tool?",
    # "this" implies per-invocation approval
)
```

The UI displays the specific command arguments (lines 81-85), creating a reasonable expectation that the user is approving only that specific invocation.

Additionally, `shell_tools.py:77` passes the full process environment to every subprocess:

```python
process_env = os.environ.copy()  # includes OPENAI_API_KEY, etc.
```

There is no command filtering, blocklist, or environment variable sanitization in the shell tools module.

## PoC

```python
from praisonaiagents import Agent
from praisonaiagents.tools.shell_tools import execute_command

# Step 1: Create agent with shell tool
agent = Agent(
    name="worker",
    instructions="You are a helpful assistant.",
    tools=[execute_command]
)

# Step 2: Agent requests benign command — user sees Rich panel:
#   Function: execute_command
#   Risk Level: CRITICAL
#   Arguments:
#     command: ls -la
#   "Do you want to execute this critical risk tool?" [y/N]
# User approves → mark_approved("execute_command") is called

# Step 3: All subsequent execute_command calls bypass approval silently:
# execute_command(command="env")
#   → returns ALL environment variables (OPENAI_API_KEY, AWS_SECRET_ACCESS_KEY, etc.)
#   → NO approval prompt shown

# Step 4: Targeted extraction also bypasses approval:
# execute_command(command="printenv OPENAI_API_KEY")
#   → returns the specific API key
#   → NO approval prompt shown

# Verification: check the approval cache
from praisonaiagents.approval import is_already_approved
# After approving "ls -la":
# is_already_approved("execute_command") → True
# Any execute_command call now returns immediately at __init__.py:177-178
```

## Impact

- **Secret exfiltration**: An LLM agent (or one subjected to prompt injection) can dump all process environment variables after a single benign command approval. Common secrets include `OPENAI_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `DATABASE_URL`, and any other credentials passed via environment.
- **Misleading consent UI**: The console prompt displays specific arguments and uses language ("this tool") that implies per-invocation consent, but the system grants session-wide blanket approval.
- **No expiration or scope**: The approval cache uses a `ContextVar` that persists for the entire agent execution context with no timeout, no command-count limit, and no clearing between tool calls.
- **No environment filtering**: `os.environ.copy()` passes every environment variable to subprocesses without filtering sensitive patterns.

## Recommended Fix

1. **Per-invocation approval for critical tools** — store a hash of `(tool_name, arguments)` instead of just `tool_name`, or require re-approval for each invocation of critical-risk tools:

```python
# In registry.py — change mark_approved/is_already_approved:
import hashlib, json

def mark_approved(self, tool_name: str, arguments: dict = None) -> None:
    approved = self._approved_context.get(set())
    risk = self._risk_levels.get(tool_name)
    if risk == "critical" and arguments:
        key = f"{tool_name}:{hashlib.sha256(json.dumps(arguments, sort_keys=True).encode()).hexdigest()}"
    else:
        key = tool_name
    approved.add(key)
    self._approved_context.set(approved)

def is_already_approved(self, tool_name: str, arguments: dict = None) -> bool:
    approved = self._approved_context.get(set())
    risk = self._risk_levels.get(tool_name)
    if risk == "critical" and arguments:
        key = f"{tool_name}:{hashlib.sha256(json.dumps(arguments, sort_keys=True).encode()).hexdigest()}"
        return key in approved
    return tool_name in approved
```

2. **Filter environment variables** in `shell_tools.py`:

```python
SENSITIVE_PATTERNS = ('_KEY', '_SECRET', '_TOKEN', '_PASSWORD', '_CREDENTIAL')

process_env = {
    k: v for k, v in os.environ.items()
    if not any(p in k.upper() for p in SENSITIVE_PATTERNS)
}
if env:
    process_env.update(env)
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-ffp3-3562-8cv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-56074
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
- https://www.vulncheck.com/advisories/praisonai-tool-approval-cache-bypass-via-coarse-grained-caching
