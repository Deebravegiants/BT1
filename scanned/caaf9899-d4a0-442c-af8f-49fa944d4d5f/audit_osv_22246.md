# [C] Socket.io - Improper type validation in attachment parsing

## Summary
Severity: Critical
Advisory: CVE-2022-2421
Aliases: GHSA-qm95-pgcg-qqfq
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-10-25
Source: https://osv.dev/vulnerability/CVE-2022-2421
Type: osv

## Details
Due to improper type validation in attachment parsing the Socket.io js library, it is possible to overwrite the _placeholder object which allows an attacker to place references to functions at arbitrary places in the resulting query object.

## References
- https://csirt.divd.nl/CVE-2022-2421
- https://csirt.divd.nl/DIVD-2022-00045
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2421.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2421
