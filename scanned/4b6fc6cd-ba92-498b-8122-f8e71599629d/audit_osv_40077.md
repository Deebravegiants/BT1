# [M] OpenProject: Private work package data disclosure through single meeting agenda item API

## Summary
Severity: Medium
Advisory: CVE-2026-49355
Aliases: GHSA-g387-6rm2-xw88
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-49355
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.4.0, `GET /api/v3/meetings/:meeting_id/agenda_items/:agenda_item_id` discloses private work package data from a linked work package that belongs to a private/inaccessible project. This vulnerability is fixed in 17.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49355.json
- https://github.com/opf/openproject/security/advisories/GHSA-g387-6rm2-xw88
- https://nvd.nist.gov/vuln/detail/CVE-2026-49355
