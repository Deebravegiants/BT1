# [M] Joplin Server delta API returns note content after share access is revoked

## Summary
Severity: Medium
Advisory: CVE-2026-34600
Aliases: GHSA-88x4-77rc-jw94
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-34600
Type: osv

## Details
Joplin is an open source note-taking and to-do application that organises notes and lists into notebooks. Versions 3.5.2 and prior contain a logic error in the delta API that allows share recipients to download notes that are no longer shared with them, related to but not fully fixed by the prior patch in #14289. In ChangeModel.delta, when DELTA_INCLUDES_ITEMS is enabled (the default), the latest state of items is attached to delta output without verifying that those items are still shared with the requesting user, and the existing removal logic only filters items deleted for all users. Additionally, the change compression logic incorrectly reduces create - delete to NOOP, which is unsafe because compression is applied per page and an item can have multiple create events; if an earlier create falls on a separate page from a later create -> delete pair, the deletion is dropped and the sequence collapses to a create. As a result, the delta API returns a create event for a deleted item with the full latest content attached, exposing notes the user no longer has access to. This issue has been fixed in version 3.5.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34600.json
- https://github.com/laurent22/joplin/security/advisories/GHSA-88x4-77rc-jw94
- https://nvd.nist.gov/vuln/detail/CVE-2026-34600
- https://github.com/laurent22/joplin/issues/14110
- https://github.com/laurent22/joplin/pull/14289
