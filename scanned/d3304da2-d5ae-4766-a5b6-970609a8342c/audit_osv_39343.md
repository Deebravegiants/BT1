# [M] Nextcloud: Missing permission check for from submissions

## Summary
Severity: Medium
Advisory: CVE-2026-45267
Aliases: GHSA-r4gh-f8x6-m55f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45267
Type: osv

## Details
Nextcloud is an open source content collaboration platform. Prior to version 5.2.6, a missing permissions check allowed users to request reading form submissions of other users. This issue has been patched in version 5.2.6.

## References
- https://hackerone.com/reports/3628817
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45267.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-r4gh-f8x6-m55f
- https://nvd.nist.gov/vuln/detail/CVE-2026-45267
- https://github.com/nextcloud/forms/pull/3269
