# [M] Icinga 2 API users could access restricted values in filter expressions

## Summary
Severity: Medium
Advisory: CVE-2025-61907
Aliases: GHSA-gg32-w9rm-vp2v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-61907
Type: osv

## Details
Icinga 2 is an open source monitoring system. In Icinga 2 versions 2.4 through 2.15.0, filter expressions provided to the various /v1/objects endpoints could access variables or objects that would otherwise be inaccessible for the user. This allows authenticated API users to learn information that should be hidden from them, including global variables not permitted by the variables permission and objects not permitted by the corresponding objects/query permissions. The vulnerability is fixed in versions 2.15.1, 2.14.7, and 2.13.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61907.json
- https://github.com/Icinga/icinga2/security/advisories/GHSA-gg32-w9rm-vp2v
- https://nvd.nist.gov/vuln/detail/CVE-2025-61907
- https://github.com/Icinga/icinga2/commit/56255ac7a689b9e198742d2fca6f7459a54c85a3
