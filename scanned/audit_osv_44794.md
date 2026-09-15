# [M] MISP UiBeta Collection View Bypasses Event ACL, Exposing Unauthorized Event Data

## Summary
Severity: Medium
Advisory: CVE-2026-86283
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/CVE-2026-86283
Type: osv

## Details
MISP's UiBeta theme collection view (app/View/Themed/UiBeta/Collections/view.ctp) performed a secondary query of member events by UUID without applying the caller's access control list (ACL). The CollectionsController::view() action correctly resolved collection element UUIDs through Event::fetchSimpleEvents($user, ...), which enforces per-user event ACL. However, the view template independently re-queried the same UUIDs using only an Event.uuid IN (...) condition, omitting the createEventConditions() authorization filter. Because collection element UUIDs are stored without server-side authorization against the referenced event (CollectionElementsController::add() accepts whatever UUID the collection owner posts), an authenticated user with view access to a collection could retrieve full details of events they are not permitted to read. The exposed data included event identifiers, info, dates, timestamps, creator organization, all event tags, and galaxy clusters (the latter attached via a cluster-scoped rather than event-scoped ACL check). This constitutes an authorization bypass at the presentation layer, allowing horizontal privilege escalation across event boundaries within the MISP instance.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86283.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86283
- https://github.com/MISP/MISP/commit/44573e4a8
- https://github.com/MISP/MISP
