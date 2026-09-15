# [C] BBOT's various issues in unarchive.py can cause arbitrary file write and RCE

## Summary
Severity: Critical
Advisory: GHSA-fhw8-8v9p-7jp7
CVE: CVE-2025-10284
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-fhw8-8v9p-7jp7
Type: github-advisory

## Affected
- PyPI: `bbot` — affected >=0 <2.7.0

## Details
### Summary

Various issues in bbot's `unarchive.py` allow a malicious site to cause bbot to write arbitrary files to arbitrary locations. This can be used to achieve Remote Code Execution (RCE).

### Impact

A user who uses bbot to scan a malicious webserver may have arbitrary code executed on their system.

## References
- https://github.com/blacklanternsecurity/bbot/security/advisories/GHSA-fhw8-8v9p-7jp7
- https://nvd.nist.gov/vuln/detail/CVE-2025-10284
- https://github.com/blacklanternsecurity/bbot/commit/6325f2f4f8f6f4545703e4c9b8004e69f71bec82
- https://blog.blacklanternsecurity.com/p/bbot-security-advisory-gitdumper
- https://github.com/blacklanternsecurity/bbot
