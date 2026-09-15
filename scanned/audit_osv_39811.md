# [M] CVAT: Missing path-containment validation in multiple entry points allows arbitrary path writes

## Summary
Severity: Medium
Advisory: CVE-2026-47682
Aliases: GHSA-6f87-4g86-p9gw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-47682
Type: osv

## Details
CVAT is an open source interactive video and image annotation tool for computer vision. In versions 1.6.0 through 2.64.0, an attacker with write access to a cloud storage that's been added to a CVAT instance, or ability to add new cloud storages, is able to overwrite arbitrary files on the server's filesystem. This issue has been fixed in version 2.65.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47682.json
- https://github.com/cvat-ai/cvat/security/advisories/GHSA-6f87-4g86-p9gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-47682
- https://github.com/cvat-ai/cvat/commit/6fda3e3285a185ae50039d1af8c8f0e9319b671c
