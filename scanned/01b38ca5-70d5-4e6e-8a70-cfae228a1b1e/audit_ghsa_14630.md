# [M] Marp Core allows XSS by improper neutralization of HTML sanitization

## Summary
Severity: Medium
Advisory: GHSA-x52f-h5g4-8qv5
CVE: CVE-2024-56510
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-12-26
Source: https://github.com/advisories/GHSA-x52f-h5g4-8qv5
Type: github-advisory

## Affected
- npm: `@marp-team/marp-core` — affected >=3.0.2 <3.9.1
- npm: `@marp-team/marp-core` — affected >=4.0.0 <4.0.1

## Details
Marp Core ([`@marp-team/marp-core`](https://www.npmjs.com/package/@marp-team/marp-core)) from v3.0.2 to v3.9.0 and v4.0.0, are vulnerable to cross-site scripting (XSS)  due to improper neutralization of HTML sanitization.

### Impact

Marp Core includes an HTML sanitizer with allowlist support. In the affected versions, the built-in allowlist is enabled by default. When the allowlist is active, if insufficient HTML comments are included, the sanitizer may fail to properly sanitize HTML content and lead cross-site scripting (XSS).

### Patches

Marp Core [v3.9.1](https://github.com/marp-team/marp-core/releases/tag/v3.9.1) and [v4.0.1](https://github.com/marp-team/marp-core/releases/tag/v4.0.1) have been patched to fix that.

### Workarounds

If you are unable to update the package immediately, disable all HTML tags by setting `html: false` option in the `Marp` class constructor.

```javascript
const marp = new Marp({ html: false })
```

### References

- [CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')](https://cwe.mitre.org/data/definitions/79.html)
- https://github.com/marp-team/marp-core/pull/282
- https://github.com/marp-team/marp-core/commit/61a1def244d1b6faa8e2c0be97ec0b68cab3ab49

### Credits

Thanks to @Ry0taK for finding out this vulnerability.

## References
- https://github.com/marp-team/marp-core/security/advisories/GHSA-x52f-h5g4-8qv5
- https://nvd.nist.gov/vuln/detail/CVE-2024-56510
- https://github.com/marp-team/marp-core/pull/282
- https://github.com/marp-team/marp-core/commit/61a1def244d1b6faa8e2c0be97ec0b68cab3ab49
- https://github.com/marp-team/marp-core
- https://github.com/marp-team/marp-core/releases/tag/v3.9.1
- https://github.com/marp-team/marp-core/releases/tag/v4.0.1
