# [M] Claude SDK for Python: Memory Tool Path Validation Race Condition Allows Sandbox Escape

## Summary
Severity: Medium
Advisory: GHSA-w828-4qhx-vxx3
CVE: CVE-2026-34452
CWE: CWE-367, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-w828-4qhx-vxx3
Type: github-advisory

## Affected
- PyPI: `anthropic` — affected >=0.86.0 <0.87.0

## Details
The async local filesystem memory tool in the Anthropic Python SDK validated that model-supplied paths resolved inside the sandboxed memory directory, but then returned the unresolved path for subsequent file operations. A local attacker able to write to the memory directory could retarget a symlink between validation and use, causing reads or writes to escape the sandbox. The synchronous memory tool implementation was not affected.

Users on the affected versions are advised to update to the latest version.

Claude SDK for Python thanks [hackerone.com/kasthelord](https://hackerone.com/kasthelord) for reporting this issue!

## References
- https://github.com/anthropics/anthropic-sdk-python/security/advisories/GHSA-w828-4qhx-vxx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-34452
- https://github.com/anthropics/anthropic-sdk-python/commit/6599043eee6e86dce16953fcd1fd828052052be6
- https://github.com/anthropics/anthropic-sdk-python
- https://github.com/anthropics/anthropic-sdk-python/releases/tag/v0.87.0
