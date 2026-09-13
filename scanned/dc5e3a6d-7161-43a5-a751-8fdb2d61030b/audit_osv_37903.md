# [M] EspoCRM: Email importEml can import and delete another user's attachment by raw fileId

## Summary
Severity: Medium
Advisory: CVE-2026-33740
Aliases: GHSA-wr7j-hxf8-hc4w
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-33740
Type: osv

## Details
EspoCRM is an open source customer relationship management application. In versions 9.3.3 and below, the POST /api/v1/Email/importEml endpoint contains an Insecure Direct Object Reference (IDOR) vulnerability where the attacker-supplied fileId parameter is used to fetch any attachment directly from the repository without verifying that the current user has authorization to access it. Any authenticated user with Email:create and Import permissions can exploit this to read another user's .eml attachment contents by importing them as a new email into the attacker's mailbox, while the original victim attachment record is deleted as a side effect of the import flow. This is inconsistent with the standard attachment download path, which enforces ACL checks before returning file data, and is practically exploitable because attachment IDs are commonly exposed in normal UI and API workflows such as stream payloads and download links. This issue is fixed in version 9.3.4.

## References
- https://github.com/espocrm/espocrm/releases/tag/9.3.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33740.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-wr7j-hxf8-hc4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33740
- https://github.com/espocrm/espocrm/commit/88e3ba6a7b5cab5dbc2298e2a093d3aa383aa95f
