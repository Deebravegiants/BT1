# [H] @rhinostone/swig: arbitrary local file read via include/extends path traversal

## Summary
Severity: High
Advisory: GHSA-2mf3-mr2r-r4vf
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-2mf3-mr2r-r4vf
Type: github-advisory

## Affected
- npm: `@rhinostone/swig` — affected >=0 <2.7.1
- npm: `@rhinostone/swig-core` — affected >=0 <2.7.1
- npm: `@rhinostone/swig-twig` — affected >=0 <2.7.1
- npm: `@rhinostone/swig-jinja2` — affected >=0 <2.7.1
- npm: `@rhinostone/swig-django` — affected >=0 <2.7.1

## Details
### Overview

`@rhinostone/swig` is a maintained fork of the abandoned `swig` template engine and inherited the directory-traversal vulnerability tracked upstream as CVE-2023-25345 / GHSA-2rq5-699j-x7p6. The `{% include %}`, `{% extends %}`, and `{% import %}` tags resolve their target path through the filesystem loader without confining the result to the configured template root. A path that traverses upward (`../`) escapes the root and reads an arbitrary file from the host filesystem, whose contents are emitted into the rendered output.

### Attack scenario

The dangerous case does **not** require the attacker to control template source — only template **data** (the `locals` passed at render time). An application that renders a trusted template whose include / extends path is variable-driven is exposed:

```js
// application code — a configured filesystem loader with a basepath
swig.renderFile('page.html', { partial: req.query.partial });
```

```
{# page.html — trusted template #}
{% include partial %}
```

Setting `?partial=../../../../etc/passwd` makes the loader resolve and read that file, and its contents are rendered into the response. A literal in trusted source is equally affected: `{% include "../../../etc/passwd" %}`.

### Impact

Arbitrary local file disclosure (confidentiality). An attacker able to influence an include / extends / import path — directly, or via untrusted `locals` — can read files outside the template directory: application configuration, credentials, source code, `/etc/passwd`, and so on. There is no integrity or availability impact.

### Affected & patched

Every published version up to and including `2.7.0` is affected — `@rhinostone/swig`, and the shared `@rhinostone/swig-core` loader, hence `@rhinostone/swig-twig`, `@rhinostone/swig-jinja2`, and `@rhinostone/swig-django` as well.

Fixed in **`2.7.1`**: the filesystem loader now rejects any `include` / `extends` / `import` path that resolves outside the configured `basepath` root, including paths supplied through an untrusted runtime variable. A new `allowOutsideRoot` loader option is available for the rare case of intentionally reading files from outside the root.

**Upgrade to `2.7.2` or later:** `2.7.1` fixed the vulnerability but introduced a regression — a *relative* `basepath` wrongly rejected every in-root template path. `2.7.2` resolves the `basepath` to an absolute path before the check and restores correct in-root resolution.

### Workarounds

- Upgrade to `2.7.2` (or later).
- If you cannot upgrade immediately: configure the filesystem loader with an explicit `basepath`, and never pass untrusted data into an `{% include %}` / `{% extends %}` / `{% import %}` path.

### References

- GHSA-2rq5-699j-x7p6 — https://github.com/advisories/GHSA-2rq5-699j-x7p6
- CVE-2023-25345 (NVD) — https://nvd.nist.gov/vuln/detail/CVE-2023-25345
- Upstream issue (swig-templates) — https://github.com/node-swig/swig-templates/issues/88
- Fix commit — https://github.com/gina-io/swig/commit/381bdc305e0b10e45368d56324328b9b4f7017fc

## References
- https://github.com/gina-io/swig/security/advisories/GHSA-2mf3-mr2r-r4vf
- https://nvd.nist.gov/vuln/detail/CVE-2023-25345
- https://github.com/gina-io/swig/commit/381bdc305e0b10e45368d56324328b9b4f7017fc
- https://github.com/gina-io/swig
