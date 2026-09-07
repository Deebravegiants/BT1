# [C] Dolibarr remote PHP code execution

## Summary
Severity: Critical
Advisory: GHSA-vxr9-p2xw-m8cf
CVE: CVE-2021-33816
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vxr9-p2xw-m8cf
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=13.0.2 <14.0.0

## Details
The website builder module in Dolibarr 13.0.2 allows remote PHP code execution because of an incomplete protection mechanism in which system, exec, and shell_exec are blocked but backticks are not blocked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33816
- https://github.com/Dolibarr/dolibarr
- https://trovent.github.io/security-advisories/TRSA-2106-01/TRSA-2106-01.txt
- https://trovent.io/security-advisory-2106-01
- http://seclists.org/fulldisclosure/2021/Nov/39
