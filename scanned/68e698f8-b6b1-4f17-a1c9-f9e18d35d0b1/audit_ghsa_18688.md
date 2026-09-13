# [C] BBOT's insufficient sanitization issues in gitdumper.py can lead to RCE

## Summary
Severity: Critical
Advisory: GHSA-h6m2-r6h9-4c44
CVE: CVE-2025-10283
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-h6m2-r6h9-4c44
Type: github-advisory

## Affected
- PyPI: `bbot` — affected >=0 <2.7.0

## Details
### Summary

bbot's `gitdumper.py` insufficiently sanitises a `.git/config` file, leading to Remote Code Execution (RCE).

bbot's `gitdumper.py` can be made to consume a malicious `.git/index` file, leading to arbitrary file write which can be used to achieve Remote Code Execution (RCE).

### Impact

A user who uses bbot to scan a malicious webserver may have arbitrary code executed on their system.

## References
- https://github.com/blacklanternsecurity/bbot/security/advisories/GHSA-h6m2-r6h9-4c44
- https://nvd.nist.gov/vuln/detail/CVE-2025-10283
- https://github.com/blacklanternsecurity/bbot/commit/0ede97fa887de33fcfd1378b4213a09c21dc6140
- https://blog.blacklanternsecurity.com/p/bbot-security-advisory-gitdumper
- https://github.com/blacklanternsecurity/bbot
