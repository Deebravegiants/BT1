# [M] Craft CMS: Authorization bypass in `entries/move-to-section` via missing target-section save check

## Summary
Severity: Medium
Advisory: GHSA-43cq-c2gq-pfpw
CVE: CVE-2026-50280
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-43cq-c2gq-pfpw
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.21

## Details
### Summary

The `EntriesController::actionMoveToSection()` endpoint checks only whether the current user can view the destination section, but it does not require permission to save entries into that section. A low-privileged authenticated control-panel user who can move an entry out of its current section can therefore move that entry into a different section where they have read access but no write access.

### Details

The vulnerable route is implemented in [EntriesController.php](/D:/files/projects/cms-5.9.19/cms-5.9.19/src/controllers/EntriesController.php):465:

The destination check is only `viewEntries:$section->uid` . The source-entry gate is `Entry::canMove()`, which verifies whether the user can move the existing entry based on the source section:

This closes the exploit chain:

1. External source: authenticated CP request to `entries/move-to-section`.
2. Missing authorization check: destination section requires only `viewEntries`, not `saveEntries`.
3. Privileged sink: `moveEntryToSection()` rewrites `sectionId` and saves the entry into the unauthorized section.

Preconditions derived from the code:

1. The attacker is authenticated to the control panel.
2. Entry `345` is movable by the attacker from its current section.
3. The attacker can satisfy `viewEntries` on destination section `12`.
4. The attacker does not have `saveEntries:DESTINATION_UID`, which is the missing check that makes the bypass possible.

Result:

1. The controller accepts the request because `viewEntries:$section->uid` passes.
2. Each source entry passes `canMove()` based on source-section permissions.
3. `moveEntryToSection()` updates the entry’s `sectionId` and saves it.
4. The entry is now located in a section where the attacker did not have write permission.

### Impact

This breaks the intended section-level authorization model. A user with limited content permissions can inject or relocate content into a protected section, interfering with editorial boundaries, approval workflows, section-specific business logic, and content ownership expectations.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-43cq-c2gq-pfpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-50280
- https://github.com/craftcms/cms/commit/0a6b916f6367b0162b2eaf2366add67b45fa98ea
- https://github.com/craftcms/cms
