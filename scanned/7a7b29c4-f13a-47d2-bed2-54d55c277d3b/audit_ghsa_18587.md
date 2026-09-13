# [M] PowerJob OpenAPIController is missing authorization 

## Summary
Severity: Medium
Advisory: GHSA-9wq6-87hw-6mhc
CVE: CVE-2025-11581
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-9wq6-87hw-6mhc
Type: github-advisory

## Affected
- Maven: `tech.powerjob:powerjob-server-starter` — affected >=0

## Details
A security vulnerability has been detected in PowerJob up to 5.1.2. This vulnerability affects unknown code of the file /openApi/runJob of the component OpenAPIController. Such manipulation leads to missing authorization. The attack can be launched remotely. The exploit has been disclosed publicly and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11581
- https://github.com/PowerJob/PowerJob/issues/1128
- https://github.com/PowerJob/PowerJob
- https://vuldb.com/?ctiid.327903
- https://vuldb.com/?id.327903
- https://vuldb.com/?submit.662558
