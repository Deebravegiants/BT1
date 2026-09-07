# [M] Cross-site Scripting in DayByDay CRM

## Summary
Severity: Medium
Advisory: GHSA-jr37-66pj-36v7
CVE: CVE-2022-22109
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-jr37-66pj-36v7
Type: github-advisory

## Affected
- Packagist: `bottelet/flarepoint` — affected >=0 <2.2.1

## Details
In Daybyday CRM, version 2.2.0 is vulnerable to Stored Cross-Site Scripting (XSS) vulnerability that allows low privileged application users to store malicious scripts in the title field of new tasks. These scripts are executed in a victim’s browser when they open the “/tasks” page to view all the tasks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22109
- https://github.com/Bottelet/DaybydayCRM/commit/002dc75f400cf307bd00b71a5a93f1e26e52cee2
- https://github.com/Bottelet/DaybydayCRM
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-22109
