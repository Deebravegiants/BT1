# [C] PraisonAI Has Path Traversal in FileTools

## Summary
Severity: Critical
Advisory: GHSA-693f-pf34-72c5
CVE: CVE-2026-35615
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-693f-pf34-72c5
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <1.5.113

## Details
### Executive Summary:
The path validation has a critical logic bug: it checks for `..` AFTER `normpath()` has already collapsed all `..` sequences. This makes the check completely useless and allows trivial path traversal to any file on the system.
The path validation function also does not resolve the symlink wich could potentially cause path traversal.

### Details:
`_validate_path()` calls `os.path.normpath()` first, which collapses `..` sequences, then checks for `'..'` in normalized. Since `..` is already collapsed, the check always passes.

**Vulnerable File:**
`src/praisonai-agents/praisonaiagents/tools/file_tools.py`

**Lines:**
42-49

```python
class FileTools:
    """Tools for file operations including read, write, list, and information."""
    
    @staticmethod
    def _validate_path(filepath: str) -> str:
        # Normalize the path
        normalized = os.path.normpath(filepath)
        absolute = os.path.abspath(normalized)
        
        # Check for path traversal attempts (.. after normalization)
        # We check the original input for '..' to catch traversal attempts
        if '..' in normalized:
            raise ValueError(f"Path traversal detected: {filepath}")
        
        return absolute
```

**Severity:** CRITICAL

**CVSS v3.1:** 9.2 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N

**CWE:** CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')

### Proof of concept (PoC)

**Prerequisites:**
- Ability to specify a file path can call file operations

**Steps to reproduce:**
poc.py
```python
from praisonaiagents.tools.file_tools import FileTools

print(FileTools._validate_path('/tmp/../etc/passwd'))
# Returns: /etc/passwd

print(FileTools.read_file('/tmp/../etc/passwd'))
# Returns: content of /etc/passwd
```

**Why this works:**
```python
# Current vulnerable code:
normalized = os.path.normpath(filepath)  # Collapses .. HERE
absolute = os.path.abspath(normalized)
if '..' in normalized:  # Check AFTER collapse - ALWAYS FALSE!
    raise ValueError(...)
```

### Impact:
- **Complete bypass** of path traversal protection
- Access to ANY file on the system with path from any starting directory
- Read sensitive files: `/etc/passwd`, `/etc/shadow`, `~/.ssh/id_rsa`
- Write arbitrary files if combined with write operations
- Affect file operations `read_file`, `write_file`, `list_files`, `get_file_info`, `copy_file`, `move_file`, `delete_file`, `download_file`


### Additional Notes:
- **Fix:** Check for `'..' in filepath` BEFORE calling `normpath()`, not after
- `_validate_path` uses `os.path.normpath` and `os.path.abspath`, which don't resolve symlinks, making it vulnerable to path traversal via symlink if attacker can control the symlink.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-693f-pf34-72c5
- https://nvd.nist.gov/vuln/detail/CVE-2026-35615
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.113
