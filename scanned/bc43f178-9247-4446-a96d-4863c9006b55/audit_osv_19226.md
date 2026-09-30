# [M] CVE-2020-8890

## Summary
Severity: Medium
Advisory: CVE-2020-8890
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-8890
Type: osv

## Details
An issue was discovered in MISP before 2.4.121. It mishandled time skew (between the machine hosting the web server and the machine hosting the database) when trying to block a brute-force series of invalid requests.

## References
- https://github.com/MISP/MISP/commit/934c82819237b4edf1da64587b72a87bec5dd520
- https://github.com/MISP/MISP/commit/c1a0b3b2809b21b4df8c1efbc803aff700e262c3
- https://github.com/MISP/MISP/compare/v2.4.120...v2.4.121
