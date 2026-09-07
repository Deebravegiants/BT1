# [M] Weblate: Stored HTML injection in editor search preview

## Summary
Severity: Medium
Advisory: GHSA-6wxc-8mgq-w26m
CVE: CVE-2026-45106
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-6wxc-8mgq-w26m
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <2026.5

## Details
### Impact
Weblate's live search preview renders unit `source` and `context` as HTML without escaping. Any contributor whose content reaches those fields stores HTML and CSS that runs inside the authenticated editor of every user who runs a matching search.

### Patches
* https://github.com/WeblateOrg/weblate/pull/19422

### Workarounds
Only the search preview on the selected views is affected.

### Resources
Weblate thanks @adrgs for reporting this issue responsibly via GitHub.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-6wxc-8mgq-w26m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45106
- https://github.com/WeblateOrg/weblate/pull/19422
- https://github.com/WeblateOrg/weblate/commit/8b0adf1d0b43dfc0d09da4b878857b2288b84f2d
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-2026.5
