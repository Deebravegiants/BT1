# [H] Parse Server vulnerable to stored cross-site scripting (XSS) via SVG file upload

## Summary
Severity: High
Advisory: GHSA-hcj7-6gxh-24ww
CVE: CVE-2026-30948
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-hcj7-6gxh-24ww
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.5.2-alpha.4
- npm: `parse-server` — affected >=0 <8.6.17

## Details
### Impact

A stored cross-site scripting (XSS) vulnerability allows any authenticated user to upload an SVG file containing JavaScript. The file is served inline with `Content-Type: image/svg+xml` and without protective headers, causing the browser to execute embedded scripts in the Parse Server origin. This can be exploited to steal session tokens from `localStorage` and achieve account takeover.

The default `fileExtensions` option blocks HTML file extensions but does not block SVG, which is a well-known XSS vector. All Parse Server deployments where file upload is enabled for authenticated users (the default) are affected.

### Patches

The fix adds `svg` (case-insensitive) to the default file extension denylist. The default regex changes from `^(?![xXsS]?[hH][tT][mM][lL]?$)` to `^(?!([xXsS]?[hH][tT][mM][lL]?|[sS][vV][gG])$)`.

### Workarounds

Configure the `fileExtensions` option to explicitly block SVG uploads:

```js
{
  fileUpload: {
    fileExtensions: ['^(?!([xXsS]?[hH][tT][mM][lL]?|[sS][vV][gG])$)']
  }
}
```

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-hcj7-6gxh-24ww
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.4
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.17

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-hcj7-6gxh-24ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-30948
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.17
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.4
