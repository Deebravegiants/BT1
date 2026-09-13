# [M] IDOR vulnerability exists in metersphere

## Summary
Severity: Medium
Advisory: CVE-2023-30550
Aliases: GHSA-j5cq-cpw2-gp2q
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-05-04
Source: https://osv.dev/vulnerability/CVE-2023-30550
Type: osv

## Details
MeterSphere is an open source continuous testing platform, covering functions such as test tracking, interface testing, UI testing, and performance testing. This IDOR vulnerability allows the administrator of a project to modify other projects under the workspace. An attacker can obtain some operating permissions. The issue has been fixed in version 2.9.0.

## References
- https://github.com/metersphere/metersphere/releases/tag/v2.9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30550.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-j5cq-cpw2-gp2q
- https://nvd.nist.gov/vuln/detail/CVE-2023-30550
