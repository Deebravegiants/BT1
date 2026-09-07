# [H] Aim Cross-Site Request Forgery vulnerability allows user to delete runs and perform other operations

## Summary
Severity: High
Advisory: GHSA-99w2-67h8-5948
CVE: CVE-2024-2196
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-99w2-67h8-5948
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
aimhubio/aim is vulnerable to Cross-Site Request Forgery (CSRF), allowing attackers to perform actions such as deleting runs, updating data, and stealing data like log records and notes without the user's consent. The vulnerability stems from the lack of CSRF and CORS protection in the aim dashboard. An attacker can exploit this by tricking a user into executing a malicious script that sends unauthorized requests to the aim server, leading to potential data loss and unauthorized data manipulation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2196
- https://github.com/aimhubio/aim
- https://huntr.com/bounties/e141e3f2-afbb-405f-a891-f66628c8b68f
