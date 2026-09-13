# [M] OpenProject has Improper Access Control on User Management allows user managers to lock admin accounts

## Summary
Severity: Medium
Advisory: CVE-2026-24777
Aliases: GHSA-fq66-cwg6-qq69
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24777
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to 17.0.2, users with the Manage Users permission can lock and unlock users. This functionality should only be possible for users of the application, but they were not supposed to be able to lock application administrators. Due to a missing permission check this logic was not enforced. The problem was fixed in OpenProject 17.0.2The problem was fixed in OpenProject 17.0.2.

## References
- https://github.com/opf/openproject/releases/tag/v17.0.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24777.json
- https://github.com/opf/openproject/security/advisories/GHSA-fq66-cwg6-qq69
- https://nvd.nist.gov/vuln/detail/CVE-2026-24777
