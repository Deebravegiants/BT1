# [M] Winter: Local File Inclusion through @import directives in LESS compilation of backend customizable stylesheets and theme assets

## Summary
Severity: Medium
Advisory: GHSA-58fp-mcx6-7qf9
CVE: CVE-2026-63179
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-58fp-mcx6-7qf9
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=0 <1.2.13

## Details
### Impact

Affected versions of Winter CMS allow authenticated backend users with the following permissions to disclose arbitrary files readable by the PHP process by injecting `@import (inline) "<path>"` directives into LESS source that the backend compiles. Four entry points share the same root cause:

- **Brand Settings** `BrandSetting.custom_css` field (`backend.manage_branding`) — compiled inline into every backend page's `<style>` block.
- **Editor Settings** `EditorSetting.html_custom_styles` field (`backend.manage_editor`) — compiled inline into every backend page's `<style>` block.
- **Mail Brand Settings** `MailBrandSetting` colour-picker fields (`system.manage_mail_templates`) — values are concatenated into LESS source via `Less_Parser::ModifyVars()` with no escaping, so any value the form validator does not reject can carry an `@import` directive.
- **Theme `.less`/`.sass`/`.scss` assets** (`cms.manage_assets`) — compiled through `System\Classes\CombineAssets` when served, with the same `Less_Parser` configuration. Both absolute paths and `..` traversal escape from the asset's own tree were exploitable.

The leaked content includes any file the web process can read, most importantly the application `.env` file (disclosing `APP_KEY` and database credentials).

To actively exploit this issue, an attacker would need an authenticated backend account with one of the permissions listed above. By default these are assigned to the built-in Developer role.

### Patches

The root cause is in the `wikimedia/less.php` integration in [Winter Storm](https://github.com/wintercms/storm): `Less_Parser` was instantiated without a safe import resolver, and its `Less_FileManager::getFilePath()` falls back to the raw attacker-supplied path when no candidate root matches. Storm now ships a `LessImportResolver` that uses the callable form of `Less_Parser::SetImportDirs()` to refuse any `@import` whose resolved path lies outside the calling context's allowed roots, defeating both absolute paths and `..` traversal at the parser level.

The four sinks have been updated to use the resolver. The three settings models pass no allowed roots (deny-all) because the bundled stylesheets ship no `@import` directives and the user fields have no legitimate use for them. `System\Classes\CombineAssets` configures the theme-asset compiler with `themes_path()`, `plugins_path()`, and `base_path('modules')` as allowed roots, preserving real cross-tree imports observed in shipped themes and plugins.

This security issue has been fixed in [v1.2.13](https://github.com/wintercms/winter/commit/130f0ea43e9228bf0d129b481da1cdfbcc4b4456) (Winter core) and [v1.2.13](https://github.com/wintercms/storm/commit/af770331c683e628533a6ec2991285d6e10a4d6c) (Winter Storm).

### Workarounds

If you cannot upgrade, apply https://github.com/wintercms/storm/commit/af770331c683e628533a6ec2991285d6e10a4d6c and https://github.com/wintercms/winter/commit/130f0ea43e9228bf0d129b481da1cdfbcc4b4456 manually. As an interim mitigation, remove `cms.manage_assets` from any non-trusted role and clear any non-empty value from the Brand Settings `custom_css` and Editor Settings `html_custom_styles` fields.

### References

See https://github.com/octobercms/october/security/advisories/GHSA-3888-q23f-x7qh for the related (but distinct in scope) October CMS advisory addressing the theme-asset compiler path. The Brand/Editor/Mail Brand Settings sinks reported in this advisory are not covered by the October patch.

Credit to Nguyen Van Hiep ([@hypnguyen1209](https://github.com/hypnguyen1209)) from Lo Security for reporting the issue.

### For more information

If you have any questions or comments about this advisory:
- Email us at [hello@wintercms.com](mailto:hello@wintercms.com)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-58fp-mcx6-7qf9
- https://github.com/wintercms/storm/commit/af770331c683e628533a6ec2991285d6e10a4d6c
- https://github.com/wintercms/winter/commit/130f0ea43e9228bf0d129b481da1cdfbcc4b4456
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.13
