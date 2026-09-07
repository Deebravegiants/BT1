# [H] Missing Authorization in DayByDay CRM

## Summary
Severity: High
Advisory: GHSA-w6rp-4vj7-v2m8
CVE: CVE-2022-22111
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-w6rp-4vj7-v2m8
Type: github-advisory

## Affected
- Packagist: `bottelet/flarepoint` — affected >=0 <2.2.1

## Details
In DayByDay CRM, version 2.2.0 is vulnerable to missing authorization. Any application user in the application who has update user permission enabled is able to change the password of other users, including the administrator’s. This allows the attacker to gain access to the highest privileged user in the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22111
- https://github.com/Bottelet/DaybydayCRM/commit/fe842ea5ede237443f1f45a99aeb839133115d8b
- https://github.com/Bottelet/DaybydayCRM
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-22111
