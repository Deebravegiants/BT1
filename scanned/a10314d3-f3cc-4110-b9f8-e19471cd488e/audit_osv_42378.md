# [H] OpenProject: Improper Access Control through /api/v3/work_packages/<X.id> via PATCH parameter "fileLinks"

## Summary
Severity: High
Advisory: CVE-2026-67527
Aliases: GHSA-c6rc-4288-8p4f
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67527
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.6.0, PATCH /api/v3/work_packages/{id} accepted _links.fileLinks and allowed authenticated users with edit_work_packages but without manage_file_links to resolve Storages::FileLink records by raw id, detach or hard-delete existing FileLinks, and re-parent FileLinks from other projects to an attacker-controlled work package, exposing origin filename, origin id, and MIME type metadata. This issue is fixed in 17.6.0.

## References
- https://github.com/opf/openproject/releases/tag/v17.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67527.json
- https://github.com/opf/openproject/security/advisories/GHSA-c6rc-4288-8p4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-67527
- https://github.com/opf/openproject/commit/db480bdeb8802e3d33e4448bb4e4b56a01de2e1f
- https://github.com/opf/openproject/pull/23815
