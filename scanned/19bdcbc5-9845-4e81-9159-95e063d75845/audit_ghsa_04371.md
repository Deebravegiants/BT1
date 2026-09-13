# [H] PraisonAI: Arbitrary File Read via `@file:` Mention Path Traversal

## Summary
Severity: High
Advisory: GHSA-2rcg-mm5h-xchx
CVE: CVE-2026-57129
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-2rcg-mm5h-xchx
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.59

## Details
## Summary

The MentionsParser in `src/praisonai-agents/praisonaiagents/tools/mentions.py` processes `@file:` mentions in agent prompts by reading arbitrary files from the filesystem. When a file path is not found relative to the workspace, the parser falls back to using the path as an absolute path without any validation or boundary check. This allows an attacker who can influence agent prompts (via chat messages, Telegram/Discord/Slack bot inputs, or YAML workflow configs) to read any file on the filesystem accessible to the process user.

## Details
**Vulnerable code (lines 165–178):**
```python
def _process_file_mention(self, file_path: str) -> Optional[str]:
    """Process @file:path mention."""
    try:
        # Resolve path relative to workspace
        full_path = self.workspace_path / file_path
        if not full_path.exists():
            # Try as absolute path
            full_path = Path(file_path)
        
        if not full_path.exists():
            self._log(f"File not found: {file_path}", logging.WARNING)
            return f"# File: {file_path}\n[File not found]"
        
        content = full_path.read_text(encoding="utf-8")
```

**The vulnerability is in the fallback at line 171–172:** When the file is not found relative to `workspace_path`, the code constructs `full_path = Path(file_path)`, which accepts any absolute or relative path without validation. There is no:
- `..` path traversal check
- Workspace boundary validation
- Symlink resolution against workspace
- Protected path guard

The `file_path` parameter originates from parsing `@file:` mentions in user/LLM prompts. The `MentionsParser` is used across the framework to process mentions in agent instructions and user messages.

**Contrast with `skill_tools.py` `read_skill_file`** (lines 140–193), which properly validates:
```python
# skill_tools.py line 179 — proper validation
if os.path.commonpath([full_path, skill_path]) != skill_path:
    return f"Error: Path traversal detected - {file_path} is outside skill directory"
```

## PoC

**Setup:** Clean checkout at commit `d5f1114a`.

**Positive trigger — arbitrary file read via @file: mention:**
```python
import sys
sys.path.insert(0, 'src/praisonai-agents')
from praisonaiagents.tools.mentions import MentionsParser

parser = MentionsParser()

# Test 1: Absolute path read (bypasses workspace resolution)
result = parser._process_file_mention('/etc/hostname')
print(f'Absolute path read: {result[:80]}...')

# Test 2: Relative path with traversal
result = parser._process_file_mention('../../../etc/hostname')
print(f'Traversal read: {result[:80]}...')
```

**Expected output:**
```
Absolute path read: # File: /etc/hostname
```linux
<hostname>
```...
Traversal read: # File: ../../../etc/hostname
```linux
<hostname>
```...
```

**Negative control — non-existent file:**
```python
result = parser._process_file_mention('/nonexistent/secret.txt')
# Returns: "# File: /nonexistent/secret.txt\n[File not found]"
```

**Cleanup:** No persistence or side effects — read-only operation.

## Impact

An attacker who can inject `@file:` mentions into agent prompts (via chat messages in Telegram/Discord/Slack bots, user input in web UI, or YAML workflow configurations) can read any file accessible to the process user, including:

- **Secrets and credentials:** `.env` files, `~/.aws/credentials`, `~/.ssh/id_rsa`, API keys
- **Configuration files:** Database passwords, JWT secrets, OAuth tokens
- **Source code:** Application internals, database schemas
- **System files:** `/etc/passwd`, `/etc/shadow` (if process has read access)

This is particularly dangerous in bot deployments where `auto_approve_tools` defaults to `True` and untrusted users can send messages containing `@file:` mentions.

## Suggested remediation

1. **Remove the absolute path fallback.** Only resolve files within `workspace_path`:
```python
def _process_file_mention(self, file_path: str) -> Optional[str]:
    full_path = (self.workspace_path / file_path).resolve()
    # Ensure resolved path is within workspace
    if not str(full_path).startswith(str(self.workspace_path.resolve())):
        return f"# File: {file_path}\n[Access denied: path outside workspace]"
    if not full_path.exists():
        return f"# File: {file_path}\n[File not found]"
    content = full_path.read_text(encoding="utf-8")
```

2. Add symlink resolution via `.resolve()` to prevent symlink-based traversal.

3. Add a protected path guard (`.env`, `.git`, `.ssh`, keys, credentials).

4. Apply the same `os.path.commonpath` pattern used by `skill_tools.py`.

### Credits
- Thai Son Dinh from VinSOC Labs (R&D)

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-2rcg-mm5h-xchx
- https://github.com/MervinPraison/PraisonAI
