# [H] Observable Timing Discrepancy in aaugustin websockets library

## Summary
Severity: High
Advisory: GHSA-8ch4-58qp-g3mp
CVE: CVE-2021-33880
CWE: CWE-203, CWE-208
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-11
Source: https://github.com/advisories/GHSA-8ch4-58qp-g3mp
Type: github-advisory

## Affected
- PyPI: `websockets` — affected >=0 <9.1

## Details
The aaugustin websockets library before 9.1 for Python has an Observable Timing Discrepancy on servers when HTTP Basic Authentication is enabled with basic_auth_protocol_factory(credentials=...). An attacker may be able to guess a password via a timing attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33880
- https://github.com/aaugustin/websockets/commit/547a26b685d08cac0aa64e5e65f7867ac0ea9bc0
- https://github.com/aaugustin/websockets
- https://github.com/pypa/advisory-database/tree/main/vulns/websockets/PYSEC-2021-95.yaml
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
