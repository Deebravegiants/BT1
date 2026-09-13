# [H] OpenLearnX has Critical Remote Code Execution Through Python Sandbox Escape via Code Execution Environment

## Summary
Severity: High
Advisory: GHSA-8h25-q488-4hxw
CVE: CVE-2026-41900
CWE: CWE-250, CWE-284, CWE-693, CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-8h25-q488-4hxw
Type: github-advisory

## Affected
- npm: `openlearnx` — affected >=0 <2.0.3

## Details
##  Overview

A critical Remote Code Execution (RCE) vulnerability was identified in the OpenLearnX code execution environment, allowing sandbox escape and arbitrary command execution. The issue has been fixed.

## References
- https://github.com/th30d4y/OpenLearnX/security/advisories/GHSA-8h25-q488-4hxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-41900
- https://github.com/th30d4y/OpenLearnX/commit/14765d7d1856d564747c55c5412e2f38feab079e
- https://github.com/th30d4y/OpenLearnX
- https://github.com/th30d4y/OpenLearnX/releases/tag/v2.0.3-security-fix
