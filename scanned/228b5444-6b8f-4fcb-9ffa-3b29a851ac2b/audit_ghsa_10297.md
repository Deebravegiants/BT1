# [M] PraisonAI has Memory State Leakage and Path Traversal in MultiAgent Context Handling

## Summary
Severity: Medium
Advisory: GHSA-766v-q9x3-g744
CVE: CVE-2026-56078
CWE: CWE-22, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-766v-q9x3-g744
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.5.115

## Details
## Summary
The `MultiAgentLedger` and `MultiAgentMonitor` components in the provided code exhibit vulnerabilities that can lead to context leakage and arbitrary file operations. Specifically:
1. **Memory State Leakage via Agent ID Collision**: The `MultiAgentLedger` uses a dictionary to store ledgers by agent ID without enforcing uniqueness. This allows agents with the same ID to share ledger instances, leading to potential leakage of sensitive context data.
2. **Path Traversal in MultiAgentMonitor**: The `MultiAgentMonitor` constructs file paths by concatenating the `base_path` and agent ID without sanitization. This allows an attacker to escape the intended directory using path traversal sequences (e.g., `../`), potentially leading to arbitrary file read/write.

## Details
### Vulnerability 1: Memory State Leakage
- **File**: `examples/context/12_multi_agent_context.py:68`
- **Description**: The `MultiAgentLedger` class uses a dictionary (`self.ledgers`) to store ledger instances keyed by agent ID. The `get_agent_ledger` method creates a new ledger only if the agent ID is not present. If two agents are registered with the same ID, they will share the same ledger instance. This violates the isolation policy and can lead to leakage of sensitive context data (system prompts, conversation history) between agents.
- **Exploitability**: An attacker can register an agent with the same ID as a victim agent to gain access to their ledger. This is particularly dangerous in multi-tenant systems where agents may handle sensitive user data.

### Vulnerability 2: Path Traversal
- **File**: `examples/context/12_multi_agent_context.py:106`
- **Description**: The `MultiAgentMonitor` class constructs file paths for agent monitors by directly concatenating the `base_path` and agent ID. Since the agent ID is not sanitized, an attacker can provide an ID containing path traversal sequences (e.g., `../../malicious`). This can result in files being created or read outside the intended directory (`base_path`).
- **Exploitability**: An attacker can create an agent with a malicious ID (e.g., `../../etc/passwd`) to write or read arbitrary files on the system, potentially leading to information disclosure or file corruption.

## PoC
### Memory State Leakage
```python
multi_ledger = MultiAgentLedger()

# Victim agent (user1) registers and tracks sensitive data
victim_ledger = multi_ledger.get_agent_ledger('user1_agent')
victim_ledger.track_system_prompt("Sensitive system prompt")
victim_ledger.track_history([{"role": "user", "content": "Secret data"}])

# Attacker registers with the same ID
attacker_ledger = multi_ledger.get_agent_ledger('user1_agent')

# Attacker now has access to victim's ledger
print(attacker_ledger.get_ledger().system_prompt)  # Outputs: "Sensitive system prompt"
print(attacker_ledger.get_ledger().history)        # Outputs: [{'role': 'user', 'content': 'Secret data'}]
```

### Path Traversal
```python
with tempfile.TemporaryDirectory() as tmpdir:
    multi_monitor = MultiAgentMonitor(base_path=tmpdir)
    
    # Create agent with malicious ID
    malicious_id = '../../malicious'
    monitor = multi_monitor.get_agent_monitor(malicious_id)
    
    # The monitor file is created outside the intended base_path
    # Example: if tmpdir is '/tmp/safe_dir', the actual path might be '/tmp/malicious'
    print(monitor.path)  # Outputs: '/tmp/malicious' (or equivalent)
```

## Impact
- **Memory State Leakage**: This vulnerability can lead to unauthorized access to sensitive agent context, including system prompts and conversation history. In a multi-tenant system, this could result in cross-user data leakage.
- **Path Traversal**: An attacker can read or write arbitrary files on the system, potentially leading to information disclosure, denial of service (by overwriting critical files), or remote code execution (if executable files are overwritten).

## Recommended Fix
### For Memory State Leakage
- Enforce unique agent IDs at the application level. If the application expects unique IDs, add a check during agent registration to prevent duplicates.
- Alternatively, modify the `MultiAgentLedger` to throw an exception if an existing agent ID is reused (unless explicitly allowed).

### For Path Traversal
- Sanitize agent IDs before using them in file paths. Replace any non-alphanumeric characters (except safe ones like underscores) or remove path traversal sequences.
- Use `os.path.join` and `os.path.realpath` to resolve paths, then check that the resolved path starts with the intended base directory.

Example fix for `MultiAgentMonitor`:
```python
import os

def get_agent_monitor(self, agent_id: str):
    # Sanitize agent_id to remove path traversal
    safe_id = os.path.basename(agent_id.replace('../', '').replace('..\\', ''))
    # Alternatively, use a strict allow-list of characters
    
    # Construct path and ensure it's within base_path
    agent_path = os.path.join(self.base_path, safe_id)
    real_path = os.path.realpath(agent_path)
    real_base = os.path.realpath(self.base_path)
    
    if not real_path.startswith(real_base):
        raise ValueError(f"Invalid agent ID: {agent_id}")
    
    ...
```
Additionally, consider using a dedicated function for sanitizing filenames.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-766v-q9x3-g744
- https://nvd.nist.gov/vuln/detail/CVE-2026-56078
- https://github.com/MervinPraison/PraisonAI
- https://www.vulncheck.com/advisories/praisonai-arbitrary-file-read-and-write-via-path-traversal-in-multiagentmonitor
