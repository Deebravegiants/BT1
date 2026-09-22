# [M]  PowerJob has Missing Authorization in its /user/list file

## Summary
Severity: Medium
Advisory: GHSA-87xj-ghmc-c3xq
CVE: CVE-2025-11580
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-87xj-ghmc-c3xq
Type: github-advisory

## Affected
- Maven: `tech.powerjob:powerjob` — affected >=0

## Details
A weakness has been identified in PowerJob up to 5.1.2. This affects the function list of the file /user/list. This manipulation causes missing authorization. The attack can be initiated remotely. The exploit has been made available to the public and could be exploited.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11580
- https://github.com/PowerJob/PowerJob/issues/1127
- https://github.com/PowerJob/PowerJob
- https://vuldb.com/?ctiid.327902
- https://vuldb.com/?id.327902
- https://vuldb.com/?submit.662446
