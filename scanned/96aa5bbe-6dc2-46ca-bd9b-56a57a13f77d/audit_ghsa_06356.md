# [M] Winter: Local File Inclusion through =include directives in JavaScript asset compilation

## Summary
Severity: Medium
Advisory: GHSA-2223-f22x-24cq
CWE: CWE-200, CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-2223-f22x-24cq
Type: github-advisory

## Affected
- Packagist: `winter/wn-system-module` — affected >=0 <1.2.13

## Details
### Impact

Affected versions of Winter CMS allow authenticated backend users with the `cms.manage_assets` permission ("Manage website assets - images, JavaScript files, CSS files") to disclose arbitrary files readable by the PHP process by placing an `=include` / `=require` directive in a theme JavaScript asset.

`Winter\Storm\Parse\Assetic\Filter\JavascriptImporter` processes `=include` / `=require` directives found in comment blocks of JavaScript assets passed through `System\Classes\CombineAssets`. The directive target was resolved relative to the including file's own directory with `realpath()` and inlined into the combined output with no confinement check, so a directive such as `=include ../../../.env` escaped the theme's asset tree and inlined an arbitrary server-readable file. The only restriction was that the target had to have a file extension, since extension-less names had `.js` appended to them.

Because the combined output is served through the `combine/{file}` route, which performs no authentication or authorization checks, the disclosed contents then became readable by **unauthenticated** visitors at a stable URL as soon as the asset was referenced by any template.

The leaked content includes any file the web process can read, most importantly the application `.env` file (disclosing `APP_KEY` and database credentials). Text files were disclosed intact; binary content was mangled by the minification pipeline.

This is the JavaScript-importer counterpart of GHSA-58fp-mcx6-7qf9 (Local File Inclusion through LESS `@import` directives) and of CVE-2023-52085 / GHSA-2x7r-93ww-cxrq — the same vulnerability class reached through a different asset combiner filter.

To actively exploit this issue, an attacker would need an authenticated backend account with the `cms.manage_assets` permission. By default this permission is assigned to the built-in Developer role. The Winter CMS maintainers strongly recommend that the `cms.manage_assets` permission only be reserved to trusted administrators and developers in general, as it grants direct write access to files that are combined and served publicly.

### Patches

`JavascriptImporter` in [Winter Storm](https://github.com/wintercms/storm) now applies two independent gates to every `=include` / `=require` target:

1. Only `.js` targets may be inlined. Any other extension is rejected before path resolution, which neutralises disclosure of non-JavaScript server files such as `.env`, `.php`, and `.log`. Extension-less includes are unaffected, as they are resolved to `.js` before this check, exactly as before.
2. The resolved path must lie within the including file's own directory subtree or one of the caller-configured allowed import roots, enforced through the new `PathResolver::withinAny()` helper. A rejected include emits a comment in place of the file contents (or throws, if the directive was `=require`).

The allowed-roots configuration is now shared between the JavaScript importer and the LESS compiler through a `HasAllowedImportRoots` trait, and `System\Classes\CombineAssets` configures both — along with the CSS `@import` filter, using the import validator added in `assetic/framework` v3.2.1 — with `themes_path()`, `plugins_path()`, and `base_path('modules')` as the allowed roots. This preserves the cross-tree imports that shipped themes and plugins legitimately use (e.g. a plugin asset importing a module asset) while confining everything else.

The backend permission descriptions for `cms.manage_assets` and `cms.manage_content` now also carry the same "should only be given to trusted users" warning that was already displayed for `cms.manage_pages`, `cms.manage_layouts`, and `cms.manage_partials`.

This security issue has been fixed in [v1.2.13](https://github.com/wintercms/winter/commit/e09c8d3526f3583cb6c3476a021b885088ecd4bd) (Winter core) and [v1.2.13](https://github.com/wintercms/storm/commit/fd673f4f32140c97c68b1ed705764b819747fbdf) (Winter Storm).

### Workarounds

If you cannot upgrade, apply https://github.com/wintercms/storm/commit/fd673f4f32140c97c68b1ed705764b819747fbdf and https://github.com/wintercms/winter/commit/e09c8d3526f3583cb6c3476a021b885088ecd4bd manually. As an interim mitigation, remove the `cms.manage_assets` permission from any role that is not held by a fully trusted administrator or developer, and audit existing theme `.js` assets for `=include` / `=require` directives that resolve outside the theme's own asset directory.

### References

- https://github.com/wintercms/winter/security/advisories/GHSA-58fp-mcx6-7qf9 — the LESS `@import` counterpart of this issue, which shares the same root cause and hardening approach.
- https://github.com/wintercms/winter/security/advisories/GHSA-2x7r-93ww-cxrq (CVE-2023-52085) — earlier Local File Inclusion through LESS compilation.

Credit to Zyad Mohamed Elmahy ([@elmahy111](https://github.com/elmahy111)) for reporting the issue.

### For more information

If you have any questions or comments about this advisory:
- Email us at [hello@wintercms.com](mailto:hello@wintercms.com)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-2223-f22x-24cq
- https://github.com/wintercms/storm/commit/fd673f4f32140c97c68b1ed705764b819747fbdf
- https://github.com/wintercms/winter/commit/e09c8d3526f3583cb6c3476a021b885088ecd4bd
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.13
