# [M] Winter: Stored XSS through cached Brand Settings and Editor Settings custom styles

## Summary
Severity: Medium
Advisory: GHSA-5cwr-5jxg-pcf6
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-5cwr-5jxg-pcf6
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=0 <1.2.14

## Details
### Impact

Users with the `backend.manage_branding` ("Customize the back-end") or `backend.manage_editor` ("Manage global code editor preferences") permission can provide custom CSS through **Settings → Customize Backend → Styles** or **Settings → Editor Settings → Markup Styles** that is compiled through the LESS CSS parser and rendered on every backend page.

v1.2.13 addressed CVE-2026-32257 and CVE-2026-32258 by applying `strip_tags()` to the compiled output of `BrandSetting::renderCss()` and `EditorSetting::renderCss()`. That fix was incomplete. Both methods cache the **raw** compiler output with `Cache::forever()` and applied `strip_tags()` only to the value returned on a cache miss, so every subsequent cache hit returned the unsanitized value directly into the backend `<style>` element. The first page render after saving therefore appears sanitized while priming an unsafe cache entry, and the stored XSS remains exploitable from the second render onwards.

Because the custom styles partial is included by both the standard backend layout head and the backend authentication layout, an injected payload also renders on the unauthenticated backend sign-in, password restore, and password reset pages.

Although this is a valid security issue, it's important to note that its severity is relatively low. To exploit the vulnerability, an attacker would already need to have trusted access to the Winter CMS backend with a specific administrative permission. The Winter CMS maintainers recommend that the `backend.manage_branding` and `backend.manage_editor` permissions only be granted to trusted administrators and developers.

All users are advised to update to the latest version to ensure their systems remain secure.

### Patches

This issue has been patched in v1.2.14. The `renderCss()` methods now apply `strip_tags()` to the cached value when it is read back, which also neutralizes any cache entry that was poisoned before upgrading.

The `backend.manage_editor` and `backend.manage_default_dashboard` permissions have additionally been given warning comments in the permission editor, matching the existing warning on `backend.manage_branding`.

### Workarounds

Apply [https://github.com/wintercms/winter/commit/c95d780ab54f3a3f74a94ae1667bf12b3c549d5d](https://github.com/wintercms/winter/commit/c95d780ab54f3a3f74a94ae1667bf12b3c549d5d) manually if unable to upgrade to v1.2.14.

Clearing the application cache removes an already-poisoned entry, but it will be recreated on the next backend page render unless the patch is applied.

### References

- CVE-2026-32257 / GHSA-v7cf-8gh9-gxmj (Stored XSS through Brand Settings custom styles, incompletely patched in v1.2.13)
- CVE-2026-32258 / GHSA-vgp4-2fc4-qff2 (Stored XSS through Editor Settings custom styles, incompletely patched in v1.2.13)
- CVE-2025-61674 and CVE-2025-61676 (identical vulnerability in October CMS, patched in v3.7.13 and v4.0.12)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-5cwr-5jxg-pcf6
- https://github.com/wintercms/winter/commit/c95d780ab54f3a3f74a94ae1667bf12b3c549d5d
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.14
