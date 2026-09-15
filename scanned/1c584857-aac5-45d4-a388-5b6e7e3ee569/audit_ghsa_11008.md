# [M] Craft CMS has an authorization bypass which allows any control panel user to move entries without permissions

## Summary
Severity: Medium
Advisory: GHSA-f582-6gf6-gx4g
CVE: CVE-2026-33162
CWE: CWE-285, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-f582-6gf6-gx4g
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.3.0 <5.9.14

## Details
### Summary

An authenticated control panel user with only accessCp can move entries across sections via POST `/actions/entries/move-to-section`, even when they do not have `saveEntries:{sectionUid}` permission for either source or destination section.

### Details

#### Root-cause analysis

  1. actionMoveToSection accepts sectionId and entryIds, loads entries, and iterates:
`Craft::$app->getEntries()->moveEntryToSection($entry, $section)`.
  2. The endpoint does not enforce per-entry or per-section authorization checks.
  3. `moveEntryToSection()` also does not enforce current-user authorization.
  4. There is a permission check in `actionMoveToSectionModalData` for building UI options, but that check is not enforced in the actual endpoint.
  5. Therefore, a direct POST request can bypass UI filtering and perform unauthorized entry moves.

 ### Impact

* This is an authorization bypass permitting unauthorized content changes.
* Authenticated low-privileged control panel users can move entries they should not be able to manage, violating integrity and potentially disrupting routing/editorial controls.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-f582-6gf6-gx4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33162
- https://github.com/craftcms/cms/commit/3c1ab1c4445dd9237855a66e6a06ecf3591a718e
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/5.9.14
