# [M] Winter: Reflected XSS through the search query parameter in the backend Table widget

## Summary
Severity: Medium
Advisory: GHSA-hq84-x37p-j6q5
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-hq84-x37p-j6q5
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=1.0.420 <1.2.14

## Details
### Impact

Affected versions of Winter CMS render the `search` query parameter without HTML encoding inside a `<script type="text/template">` block in the backend Table widget partial (`modules/backend/widgets/table/partials/_table.php`):

```php
value="<?= get('search') ?>"
```

`<script>` is an HTML raw-text context, so the surrounding `value="…"` attribute quoting is not a parser boundary. A literal `</script>` in the query string terminates the template element early, and everything after it is parsed as ordinary markup in the backend document.

Any backend page rendering a Table or DataTable widget is a sink. The value is read from the global request through the `get()` helper, which — unlike `post()` — is not restricted by HTTP method, so a plain top-level `GET` navigation is sufficient. The template is also emitted unconditionally by the partial, so widgets using the default `searching: false` configuration are equally affected.

In Winter core the reachable route is the **Editor Settings** form (`/backend/system/settings/update/winter/backend/editor`), which renders six `datatable` fields and is gated by `backend.manage_editor` — assigned by default to the built-in Developer role. Third-party plugins using the `datatable` form widget, or the Table widget directly, expose the same sink on their own pages.

An attacker who induces a signed-in backend user to follow a crafted link executes script in that user's authenticated backend origin. The injected script can read the CSRF token published in the backend layout's `<meta name="csrf-token">` element and issue credentialed requests as the victim, bounded only by that user's permissions. Because the core sink requires `backend.manage_editor`, the practical victim is a Developer-role user or superuser — who can edit CMS templates, so script running in that session can chain to server-side code execution.

This is not a permission bypass: the victim must already be authorised for the page, and the attacker gains no permission the victim does not hold.

To actively exploit this issue, an attacker needs no account of their own, but does need an authenticated backend user with access to a page rendering a Table or DataTable widget to follow an attacker-supplied link.

### Patches

The `search` value is now HTML-encoded on output, matching every other value rendered by the same partial and the equivalent handling in the backend Search widget (`modules/backend/widgets/search/partials/_search.php`):

```php
value="<?= e(get('search')); ?>"
```

This removes the raw-text terminator: the browser can no longer encounter an attacker-supplied literal `</script>` while tokenising the document. The template is subsequently parsed once by jQuery when the toolbar is built, so an encoded payload resolves to an inert attribute string rather than markup.

Regression coverage was added in `modules/backend/tests/widgets/TableSearchEscapingTest.php`, covering plain, mixed-case (`</ScRiPt>`) and whitespace-bearing (`</script >`) terminators, both `searching` states, and preservation of ordinary and Unicode search text.

This security issue has been fixed in [v1.2.14](https://github.com/wintercms/winter/commit/1b6397654124fb44a6abf6f3782b6a1d746cef14).

### Workarounds

If you cannot upgrade, apply https://github.com/wintercms/winter/commit/1b6397654124fb44a6abf6f3782b6a1d746cef14 manually — in `modules/backend/widgets/table/partials/_table.php`, change:

```php
value="<?= get('search') ?>"
```

to:

```php
value="<?= e(get('search')); ?>"
```

A restrictive Content Security Policy served at the web server or reverse proxy can reduce practical exploitability, but it is not a substitute for the fix: Winter's backend ships inline scripts, so a policy permissive enough to run the backend may still permit an injected execution primitive.

### References

Credit to Awwader ([@NRAwwad](https://github.com/NRAwwad)) for reporting the issue.

### For more information

If you have any questions or comments about this advisory:
- Email us at [hello@wintercms.com](mailto:hello@wintercms.com)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-hq84-x37p-j6q5
- https://github.com/wintercms/winter/commit/1b6397654124fb44a6abf6f3782b6a1d746cef14
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.14
