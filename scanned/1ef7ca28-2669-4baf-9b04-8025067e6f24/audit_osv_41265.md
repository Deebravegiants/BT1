# [H] Kanboard BoardAjaxController Missing Ownership Check via Drag-and-Drop

## Summary
Severity: High
Advisory: CVE-2026-58660
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-58660
Type: osv

## Details
Kanboard through 1.2.52, fixed in commit 564cc30, BoardAjaxController save() method (used by the kanban board drag-and-drop endpoint) validates the caller's role on the attacker-supplied project_id but never verifies that the supplied task_id actually belongs to that project. Because task identifiers are sequential integers shared across the entire instance, any authenticated user who is a member of at least one project can enumerate and move (corrupt/hide) tasks belonging to any other project on the same instance, including private projects they have no membership or role on.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58660.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58660
- https://www.vulncheck.com/advisories/kanboard-boardajaxcontroller-missing-ownership-check-via-drag-and-drop
- https://github.com/kanboard/kanboard/pull/5853
- https://github.com/kanboard/kanboard/commit/564cc30e1e360959572e01e158734d9475c05903
- https://github.com/kanboard/kanboard
- https://github.com/kanboard/kanboard/issues/5852
