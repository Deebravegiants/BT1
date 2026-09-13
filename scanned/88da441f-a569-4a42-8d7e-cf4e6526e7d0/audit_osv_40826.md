# [M] Grist: Insufficient access control in the /forms endpoint exposes table metadata

## Summary
Severity: Medium
Advisory: CVE-2026-55664
Aliases: GHSA-w2hc-w6cg-xvh9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55664
Type: osv

## Details
Grist is spreadsheet software using Python as its formula language. Prior to 1.7.15, the GET /forms endpoint read table and column metadata without applying the document's access rules and did not check that the requested section was actually a form. A user with only partial read access, including public access on a publicly viewable document, could request the metadata of any widget and reveal table and column structure that access rules would otherwise hide, even in documents that contain no forms. This issue is fixed in version 1.7.15.

## References
- https://github.com/gristlabs/grist-core/releases/tag/v1.7.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55664.json
- https://github.com/gristlabs/grist-core/security/advisories/GHSA-w2hc-w6cg-xvh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-55664
- https://github.com/gristlabs/grist-core/commit/14694156fe99c438c5f7a452ad367e933bb194db
