# [M] CVE-2021-41161

## Summary
Severity: Medium
Advisory: CVE-2021-41161
Aliases: GHSA-788f-g6g9-f8fc
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-04-21
Source: https://osv.dev/vulnerability/CVE-2021-41161
Type: osv

## Details
Combodo iTop is a web based IT Service Management tool. In versions prior to 3.0.0-beta6 the export CSV page don't properly escape the user supplied parameters, allowing for javascript injection into rendered csv files. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/Combodo/iTop/security/advisories/GHSA-788f-g6g9-f8fc
- https://github.com/Combodo/iTop/commit/c8f3d23d30c018bc44189b38fa34a5fffb4edb22
