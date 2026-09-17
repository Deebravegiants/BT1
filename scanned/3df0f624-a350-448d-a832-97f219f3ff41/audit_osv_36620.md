# [M] OpenProject has an IDOR on MeetingAgendaItems allows cross-project meeting agenda item transfer

## Summary
Severity: Medium
Advisory: CVE-2026-24776
Aliases: GHSA-p9v8-w9ph-hqmf
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-24776
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to 17.0.2, the drag&drop handler moving an agenda item to a different section was not properly checking if the target meeting section is part of the same meeting (or is the backlog, in case of recurring meetings). This allowed an attacker to move a meeting agenda item into a different meeting. The attacker did not get access to meetings, but they could add arbitrary agenda items, that could cause confusions. The vulnerability is fixed in 17.0.2.

## References
- https://github.com/opf/openproject/releases/tag/v17.0.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24776.json
- https://github.com/opf/openproject/security/advisories/GHSA-p9v8-w9ph-hqmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-24776
