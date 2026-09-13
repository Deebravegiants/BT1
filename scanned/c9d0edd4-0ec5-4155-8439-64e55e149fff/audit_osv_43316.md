# [H] calibre Content Server `/book-update-annotations` Missing Write Authorization Check Allows Unauthorized Annotation Modification

## Summary
Severity: High
Advisory: CVE-2026-73249
Aliases: GHSA-5x64-w63v-x2g6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73249
Type: osv

## Details
calibre is an e-book manager. Prior to 9.12.0, the calibre Content Server endpoint POST /book-update-annotations/{library_id}/{book_id}/{fmt} in src/calibre/srv/books.py omits needs_db_write=True, causing Router.dispatch() to skip ctx.check_for_write_access() before update_annotations() passes attacker-controlled JSON to db.merge_annotations_for_book(), which allows a readonly user or an anonymous user on an unauthenticated deployment to persist unauthorized book annotation changes. This issue is fixed in version 9.12.0.

## References
- https://github.com/kovidgoyal/calibre/releases/tag/v9.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73249.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-5x64-w63v-x2g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-73249
- https://github.com/kovidgoyal/calibre/commit/71295e8b62801e1ccecaa4fac47e6942f11cfe1e
