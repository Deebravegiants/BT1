# [H] i18next-fs-backend: Path traversal via unsanitised lng/ns allows arbitrary file read/overwrite

## Summary
Severity: High
Advisory: GHSA-8847-338w-5hcj
CVE: CVE-2026-41693
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-8847-338w-5hcj
Type: github-advisory

## Affected
- npm: `i18next-fs-backend` — affected >=0 <2.6.4

## Details
### Summary

Versions of `i18next-fs-backend` prior to 2.6.4 interpolate the caller-supplied `lng` and `ns` values directly into the configured `loadPath` and `addPath` templates with no path-component validation and no sanitisation. When an application exposes the resolved language code to user-controlled input (`?lng=` query parameter, cookie, request header), a crafted value can break out of the intended locale directory.

Affected call sites in `lib/index.js`:

- `read` (line 38 pre-patch): `const filename = interpolate(loadPath, { lng: language, ns: namespace })`
- `removeFile` (line 101 pre-patch): same pattern against `addPath`
- `writeFile` (line 127 pre-patch): same pattern against `addPath` for queued missing-key writes

The helper `interpolate` in `lib/utils.js` substitutes raw values with no encoding — unlike the `addQueryString` helper in `i18next-http-backend`, there is no equivalent safety for path interpolation.

### Impact

- **Arbitrary file read.** With a `loadPath` like `/locales/{{lng}}/{{ns}}.json`, an attacker-controlled `lng = '../../etc'` (and matching `ns`) causes the backend to read a file outside the locale directory. For parsers that tolerate arbitrary content (YAML's freeform text), the file contents surface as a translation resource.
- **Arbitrary file overwrite.** `addPath` is interpolated the same way for missing-key writes (the `create()` code path and the debounced writer in `writeFile`). A traversing `lng`/`ns` combination can cause the process to write JSON structures to an unintended filesystem location, potentially overwriting application files if the process user has write access.
- **Chain with `.js`/`.ts` eval.** `i18next-fs-backend` supports loading `.js` and `.ts` locale files by `eval`-ing their content (intentional feature, documented as requiring trusted sources). Combining traversal with that path — for example `lng = '../../../app/config'` against `loadPath: '/locales/{{lng}}/{{ns}}.js'` — would cause the backend to **execute** a server-side file as JavaScript, exfiltrating whatever it can touch (`process.env`, connected services).

Exploitation requires the application to pass an untrusted `lng`/`ns` value through to `i18next.t()` without its own validation. Many i18next setups do exactly this via `i18next-browser-languagedetector` (query string / cookie detection).

### Affected versions

All versions of `i18next-fs-backend` prior to **2.6.4**.

### Patch

Fixed in **2.6.4**. `lib/utils.js` now exports:

- `isSafePathSegment(v)` — returns `true` only if `v` is a non-empty string of ≤ 128 chars that does not contain `..`, `/`, `\`, control characters, or a prototype key (`__proto__`, `constructor`, `prototype`). Legitimate i18next language-code shapes (BCP-47, `en_US`, `zh-Hant-HK`, `pirate-speak`, `my-custom.ns`, `+`-joined multi-language values) all pass.
- `interpolatePath(template, data)` — substitutes variables like the existing `interpolate` but refuses the whole result if any segment fails `isSafePathSegment`. Callers bail out with an error (`read`) or silently drop the queued write (`writeFile`, `removeFile`).

The `.js` / `.ts` `eval` behaviour is intentionally retained — dynamic expressions in locale files are a documented feature of this backend, and safe replacements like dynamic `import()` are async-only and incompatible with this backend's sync-capable code path. The README has a new "Security considerations" section that spells out the trust model: `.js`/`.ts` locale files must be treated as code.

### Workarounds

No workaround short of upgrading. If you cannot upgrade immediately, sanitise `lng` / `ns` at your application boundary before passing them to i18next — reject values containing `..`, `/`, `\`, control characters, and cap the length.

### Credits

Discovered via an internal security audit of the i18next ecosystem.

## References
- https://github.com/i18next/i18next-fs-backend/security/advisories/GHSA-8847-338w-5hcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-41693
- https://github.com/i18next/i18next-fs-backend
