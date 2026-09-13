# [M] HumHub Missing Authorization on Remove All Space Members Action

## Summary
Severity: Medium
Advisory: CVE-2026-47657
Aliases: GHSA-hj67-5q6h-j7c2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47657
Type: osv

## Details
HumHub is an Open Source Enterprise Social Network. In versions 1.13.0 through 1.18.2, a missing authorization check in the Space member management controller allowed any authenticated user to trigger the removal of all members from any Space, regardless of their own role or membership in that Space. Versions 1.13.0 through 1.18.2 are affected. The vulnerability has been patched in version 1.18.3, and all users are encouraged to upgrade to this version or later immediately. No known workaround is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47657.json
- https://github.com/humhub/humhub/security/advisories/GHSA-hj67-5q6h-j7c2
- https://nvd.nist.gov/vuln/detail/CVE-2026-47657
- https://github.com/humhub/humhub/pull/8163
