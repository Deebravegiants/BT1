# [H] mingSoft MCMS File Upload vulnerability

## Summary
Severity: High
Advisory: GHSA-7qw4-9r68-2rmx
CVE: CVE-2024-22567
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-05
Source: https://github.com/advisories/GHSA-7qw4-9r68-2rmx
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
File Upload vulnerability in MCMS 5.3.5 allows attackers to upload arbitrary files via crafted POST request to /ms/file/upload.do.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22567
- https://github.com/h3ak/MCMS-CVE-Request
- https://github.com/ming-soft/MCMS
