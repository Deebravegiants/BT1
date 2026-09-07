# [M] HtmlSanitizer has a bypass via template tag

## Summary
Severity: Medium
Advisory: GHSA-j92c-7v7g-gj3f
CVE: CVE-2026-25543
CWE: CWE-116, CWE-79
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-j92c-7v7g-gj3f
Type: github-advisory

## Affected
- NuGet: `HtmlSanitizer` — affected >=0 <9.0.892
- NuGet: `HtmlSanitizer` — affected >=9.1.878-beta <9.1.893-beta

## Details
### Impact

If the `template` tag is allowed, its contents are not sanitized. The `template` tag is a special tag that does not usually render its contents, unless the `shadowrootmode` attribute is set to `open` or `closed`. 

The lack of sanitization of the template tag brings up two bypasses:

1. it is still possible to forcibly render the contents of a `<template>` tag through mutation XSS. The DOM parsers in browsers such as Chromium have a node depth limit of 512 and tags which are beyond that depth are flattened. This in turn allows elements within `<template>` (which are not sanitized) to be effectively 'popped out'. An example would look like this: `<div>[...]<template><script>alert('xss')</script>` where `[...]` denotes at least another 509 opening `<div>` tags.
2. If in addition to the template tag, the `shadowrootmode` attribute is allowed through `sanitizer.AllowedAttributes.Add("shadowrootmode");`, the simple payload of `<div><template shadowrootmode="open"><script>alert('xss')</script>` would bypass the sanitizer. This is because such usage of `<template>` attaches a shadow root to its parent: `<div>`, and its contents will be rendered. 

Note that the default configuration is not affected because the `template` tag is disallowed by default.

### Patches

The problem has been patched in versions [9.0.892](https://www.nuget.org/packages/HtmlSanitizer/9.0.892) and [9.1.893-beta](https://www.nuget.org/packages/HtmlSanitizer/9.1.893-beta).

### Workarounds

Disallow the `template` tag. It is disallowed by default.

### Resources

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/template

## References
- https://github.com/mganss/HtmlSanitizer/security/advisories/GHSA-j92c-7v7g-gj3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25543
- https://github.com/mganss/HtmlSanitizer/commit/0ac53dca30ddad963f2b243669a5066933d82b81
- https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/template
- https://github.com/mganss/HtmlSanitizer
- https://github.com/mganss/HtmlSanitizer/releases/tag/v9.0.892
- https://www.nuget.org/packages/HtmlSanitizer/9.0.892
- https://www.nuget.org/packages/HtmlSanitizer/9.1.893-beta
