# [M] league/commonmark contains a XSS vulnerability in Attributes extension

## Summary
Severity: Medium
Advisory: GHSA-3527-qv2q-pfvx
CVE: CVE-2025-46734
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-05
Source: https://github.com/advisories/GHSA-3527-qv2q-pfvx
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=1.5.0 <2.7.0

## Details
### Summary
Cross-site scripting (XSS) vulnerability in the [Attributes extension](https://commonmark.thephpleague.com/extensions/attributes/) of the league/commonmark library (versions 1.5.0 through 2.6.x) allows remote attackers to insert malicious JavaScript calls into HTML.

### Details

The league/commonmark library provides configuration options such as `html_input: 'strip'` and `allow_unsafe_links: false` to mitigate cross-site scripting (XSS) attacks by stripping raw HTML and disallowing unsafe links. However, when the Attributes Extension is enabled, it introduces a way for users to inject arbitrary HTML attributes into elements via Markdown syntax using curly braces.

As a result, even with the secure configuration shown above, an attacker can inject dangerous attributes into applications using this extension via a payload such as:

```md
![](){onerror=alert(1)}
```

Which results in the following HTML:

```html
<p><img onerror="alert(1)" src="" alt="" /></p>
```

Which causes the JS to execute immediately on page load.

### Patches

Version 2.7.0 contains three changes to prevent this XSS attack vector:

- All attributes starting with `on` are considered unsafe and blocked by default
- [Support for an explicit allowlist of allowed HTML attributes](https://commonmark.thephpleague.com/2.7/extensions/attributes/#configuration)
- Manually-added `href` and `src` attributes now respect the existing `allow_unsafe_links` configuration option

### Workarounds

If upgrading is not feasible, please consider:

- Disabling the `AttributesExtension` for untrusted users
- [Filtering the rendered HTML through a library like HTMLPurifier](https://commonmark.thephpleague.com/security/#additional-filtering)

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-3527-qv2q-pfvx
- https://nvd.nist.gov/vuln/detail/CVE-2025-46734
- https://github.com/thephpleague/commonmark/commit/f0d626cf05ad3e99e6db26ebcb9091b6cd1cd89b
- https://github.com/thephpleague/commonmark
