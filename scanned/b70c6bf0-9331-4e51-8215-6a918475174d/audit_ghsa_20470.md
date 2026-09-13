# [H] Weak Password Requirements in Daybyday CRM

## Summary
Severity: High
Advisory: GHSA-96v6-hrwg-p378
CVE: CVE-2022-22110
CWE: CWE-521
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-96v6-hrwg-p378
Type: github-advisory

## Affected
- Packagist: `bottelet/flarepoint` — affected >=1.1 <2.2.1

## Details
In Daybyday CRM, versions 1.1 through 2.2.0 enforce weak password requirements in the user update functionality. A user with privileges to update his password could change it to a weak password, such as those with a length of a single character. This may allow an attacker to brute-force users’ passwords with minimal to no computational effort.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22110
- https://github.com/Bottelet/DaybydayCRM/commit/a0392f4a4a14e1e3fedaf6817aefce69b6bd661b
- https://github.com/Bottelet/DaybydayCRM
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-22110
