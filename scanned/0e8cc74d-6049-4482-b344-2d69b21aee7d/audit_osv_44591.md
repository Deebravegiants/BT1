# [M] Craft CMS before 5.10.11 Authorization Bypass via actionDeleteForSite

## Summary
Severity: Medium
Advisory: CVE-2026-84798
Aliases: GHSA-5fh8-74j8-mvcp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84798
Type: osv

## Details
Craft CMS versions >= 5.0.0-RC1 and < 5.10.11 fail to perform an independent authorization check in ElementsController::actionDeleteForSite(). The method loads an element with checkForProvisionalDraft enabled and runs the deletion authorization check against the user's own provisional draft (which only verifies draft ownership), then propagates the deletion to the canonical element without re-checking permissions. As a result, an authenticated user who has viewEntries, viewPeerEntries, saveEntries, savePeerEntries, and editSite permissions but lacks the deleteEntriesForSite permission can hard-delete a canonical entry's site record (and, for single-site entries, the full element and content), which is irrecoverable via Craft's recycle bin.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84798.json
- https://github.com/craftcms/cms/security/advisories/GHSA-5fh8-74j8-mvcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-84798
- https://www.vulncheck.com/advisories/craft-cms-before-5.10.11-authorization-bypass-via-actiondeleteforsite
