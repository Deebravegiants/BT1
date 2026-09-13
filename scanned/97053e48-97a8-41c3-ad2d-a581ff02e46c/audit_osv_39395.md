# [M] Nextcloud: Deleting a Forms collaborator share leaves uploaded response files accessible through a lingering Files share

## Summary
Severity: Medium
Advisory: CVE-2026-45543
Aliases: GHSA-q4fw-6jf8-5vhh
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45543
Type: osv

## Details
Nextcloud is an open source content collaboration platform. From version 4.3.0 to before version 5.2.7, a removed collaborator retains unauthorized read access to uploaded respondent files for the affected form. The scope is limited to uploaded files for forms where that user previously had results access. This issue has been patched in version 5.2.7.

## References
- https://hackerone.com/reports/3617352
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45543.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-q4fw-6jf8-5vhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45543
- https://github.com/nextcloud/forms/pull/3291
