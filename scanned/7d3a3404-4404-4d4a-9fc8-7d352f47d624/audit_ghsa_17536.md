# [H] Salt has minion event bus authorization bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-jh7c-xh74-h76f
CVE: CVE-2025-22236
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-jh7c-xh74-h76f
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3007.0 <3007.4
- PyPI: `salt` — affected >=3006.0 <3006.12

## Details
Minion event bus authorization bypass. An attacker with access to a minion key can craft a message which may be able to execute a job on other minions (>= 3007.0).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22236
- https://docs.saltproject.io/en/3006/topics/releases/3006.12.html
- https://docs.saltproject.io/en/3007/topics/releases/3007.4.html
- https://github.com/saltstack/salt
