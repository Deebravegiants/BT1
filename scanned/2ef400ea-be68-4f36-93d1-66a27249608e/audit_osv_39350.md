# [M] Nextcloud: Files Lock app allows users to lock and unlock files of other users

## Summary
Severity: Medium
Advisory: CVE-2026-45283
Aliases: GHSA-4chh-6mhf-p4jj
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45283
Type: osv

## Details
Nextcloud is an open source content collaboration platform. In Nextcloud Server from versions 32.0.0 to before 32.0.2, and 33.0.0 to before 33.0.1, the files_lock app did not properly validate the ownership of files when processing DAV lock and unlock requests. An authenticated user could lock or unlock files belonging to other users by targeting their absolute WebDAV paths. Additionally, lock tokens were disclosed to unauthorized callers in error responses, allowing attackers to remove token-based locks placed by other users' client applications. It is recommended that the Nextcloud Server is upgraded to 32.0.2 or 33.0.1. It is recommended that the Nextcloud Enterprise Server is upgraded to 31.0.14.4 or 32.0.2 or 33.0.1

## References
- https://hackerone.com/reports/3301553#
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45283.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-4chh-6mhf-p4jj
- https://nvd.nist.gov/vuln/detail/CVE-2026-45283
- https://github.com/nextcloud/files_lock/pull/1007
