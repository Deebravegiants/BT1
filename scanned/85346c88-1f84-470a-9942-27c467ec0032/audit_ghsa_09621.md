# [C] PraisonAI Vulnerable to Arbitrary File Write / Path Traversal in Action Orchestrator

## Summary
Severity: Critical
Advisory: GHSA-jfxc-v5g9-38xr
CVE: CVE-2026-39305
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-jfxc-v5g9-38xr
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.113

## Details
The Action Orchestrator feature contains a Path Traversal vulnerability that allows an attacker (or compromised agent) to write to arbitrary files outside of the configured workspace directory. By supplying relative path segments (`../`) in the target path, malicious actions can overwrite sensitive system files or drop executable payloads on the host.

### Details
Location: `src/praisonai/praisonai/cli/features/action_orchestrator.py` (Lines 402, 409, 423)

Vulnerable Code snippet:
```python
target = workspace / step.target
```

In the `_apply_step` method, paths are constructed by concatenating the `workspace` path with a user-supplied `step.target` string: `target = workspace / step.target`. The code fails to resolve and validate that the final absolute path remains within the bounds of the `workspace` directory. When processing `FILE_CREATE` or `FILE_EDIT` actions, this flaw permits arbitrary file modification.

### PoC
Construct a malicious `ActionStep` payload with path traversal characters:

```python
from praisonai.cli.features.action_orchestrator import ActionStep, ActionType, ActionStatus

# Payload targeting a file outside the workspace
step = ActionStep(
    id="test_traversal",
    action_type=ActionType.FILE_CREATE,
    description="Malicious file write",
    target="../../../../../../../tmp/orchestrator_pwned.txt",
    params={"content": "pwned"},
    status=ActionStatus.APPROVED
)

# When the orchestrator applies this step, it writes to the traversed path
# _apply_step(step)
```

### Impact
This is an Arbitrary File Write vulnerability. Anyone running the Action Orchestrator to apply modifications is vulnerable. A malicious prompt could trick the agent into generating a plan that overwrites critical files (e.g., `~/.ssh/authorized_keys`, `.bashrc`) leading to Remote Code Execution (RCE) or system corruption.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-jfxc-v5g9-38xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-39305
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.113
