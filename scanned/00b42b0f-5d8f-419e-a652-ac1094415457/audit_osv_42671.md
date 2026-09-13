# [M] radare2 < 6.1.4 Project Notes Path Traversal via Symlink

## Summary
Severity: Medium
Advisory: CVE-2026-6941
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-6941
Type: osv

## Details
radare2 prior to 6.1.4 contains a path traversal vulnerability in its project notes handling that allows attackers to read or write files outside the configured project directory by importing a malicious .zrp archive containing a symlinked notes.txt file. Attackers can craft a .zrp archive with a symlinked notes.txt that bypasses directory confinement checks, allowing note operations to follow the symlink and access arbitrary files outside the dir.projects root directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6941.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6941
- https://www.vulncheck.com/advisories/radare2-project-notes-path-traversal-via-symlink
- https://github.com/radareorg/radare2/pull/25831
- https://github.com/radareorg/radare2/commit/4bcdee725ff0754ed721a98789c0af371c5f32a4
