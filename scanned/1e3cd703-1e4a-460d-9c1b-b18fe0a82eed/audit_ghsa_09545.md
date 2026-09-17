# [M] OpenClaw contains a symlink traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-35mw-5vvr-vrxc
CVE: CVE-2026-43570
CWE: CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-35mw-5vvr-vrxc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.3.22 <2026.4.5

## Details
OpenClaw versions 2026.3.22 before 2026.4.5 contain a symlink traversal vulnerability in remote marketplace repository path handling that allows attackers to escape the expected repository root. Attackers can exploit this by providing crafted symlink paths to access files outside the intended repository directory.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cr8r-7g2h-6wr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-43570
- https://github.com/openclaw/openclaw/commit/94b0062e90467e1582b47cc971f308457c537f3a
- https://github.com/openclaw/openclaw/commit/b1dd3ded3589f6fa60ab85b3930a82d538edaeae
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-symlink-traversal-in-remote-marketplace-repository-path-handling
