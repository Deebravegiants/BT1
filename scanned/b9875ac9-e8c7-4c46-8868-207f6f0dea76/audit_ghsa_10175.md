# [M] October CMS has Stored XSS in Backend Editor Markup Classes

## Summary
Severity: Medium
Advisory: GHSA-6qmh-j78v-ffp7
CVE: CVE-2026-24906
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-6qmh-j78v-ffp7
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=4.0.0 <4.1.10
- Packagist: `october/system` — affected >=0 <3.7.14

## Details
A stored cross-site scripting (XSS) vulnerability was identified in the Backend Editor Settings. The Markup Classes fields (used for paragraph styles, inline styles, table styles, etc.) did not sanitize input to valid CSS class name characters. Malicious values were rendered unsanitized in Froala editor dropdown menus, allowing JavaScript execution when any user opened a RichEditor.

### Impact
- Stored XSS via editor settings rendered in RichEditor dropdowns
- Could allow privilege escalation if a superuser opens any RichEditor (e.g., editing a blog post)
- Requires authenticated backend access with editor settings permissions
- Triggers on routine content editing operations

### Patches
The vulnerability has been patched in v3.7.14 and v4.1.10. All users are encouraged to upgrade to the latest patched version.

### Workarounds
If upgrading immediately is not possible:
- Restrict editor settings permissions to fully trusted administrators only

### References
- Reported by [Chris Alupului](https://github.com/neosprings)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-6qmh-j78v-ffp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-24906
- https://github.com/octobercms/october
