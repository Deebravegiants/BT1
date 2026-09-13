# [C] asyncmy is vulnerable to SQL injection via crafted dict keys

## Summary
Severity: Critical
Advisory: GHSA-qhqw-rrw9-25rm
CVE: CVE-2025-65896
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-qhqw-rrw9-25rm
Type: github-advisory

## Affected
- PyPI: `asyncmy` — affected >=0

## Details
SQL injection vulnerability in long2ice asyncmy thru 0.2.11 allows attackers to execute arbitrary SQL commands via crafted dict keys.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65896
- https://github.com/long2ice/asyncmy/issues/134
- https://github.com/long2ice/asyncmy
