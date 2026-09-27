# [H] FOG vulnerable to unauthenticated SSRF via `/fog/service/getversion.php`

## Summary
Severity: High
Advisory: CVE-2026-24138
Aliases: GHSA-79xw-c2qx-g7xj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-24138
Type: osv

## Details
FOG is a free open-source cloning/imaging/rescue suite/inventory management system. Versions 1.5.10.1754 and below contain an unauthenticated SSRF vulnerability in getversion.php which can be triggered by providing a user-controlled url parameter. It can be used to fetch both internal websites and files on the machine running FOG. This appears to be reachable without an authenticated web session when the request includes newService=1. The issue does not have a fixed release version at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24138.json
- https://github.com/FOGProject/fogproject/security/advisories/GHSA-79xw-c2qx-g7xj
- https://nvd.nist.gov/vuln/detail/CVE-2026-24138
