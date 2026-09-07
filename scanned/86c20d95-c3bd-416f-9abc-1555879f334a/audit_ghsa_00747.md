# [H] Cross-site scripting vulnerability in TinyMCE

## Summary
Severity: High
Advisory: GHSA-27gm-ghr9-4v95
CVE: CVE-2020-17480
CWE: CWE-79
Ecosystem: npm
Published: 2020-01-30
Source: https://github.com/advisories/GHSA-27gm-ghr9-4v95
Type: github-advisory

## Affected
- npm: `tinymce` — affected >=0 <4.9.7
- npm: `tinymce` — affected >=5.0.0 <5.1.4

## Details
### Impact
A cross-site scripting (XSS) vulnerability was discovered in: the core parser, `paste` and `visualchars` plugins. The vulnerability allowed arbitrary JavaScript execution when inserting a specially crafted piece of content into the editor via the clipboard or APIs. This impacts all users who are using TinyMCE 4.9.6 or lower and TinyMCE 5.1.3 or lower.

### Patches
This vulnerability has been patched in TinyMCE 4.9.7 and 5.1.4 by improved parser logic and HTML sanitization.

### Workarounds
The workarounds available are:
- disable the impacted plugins
- manually sanitize the content using the `BeforeSetContent` event (see below)
- upgrade to either TinyMCE 4.9.7 or TinyMCE 5.1.4

#### Example: Manually sanitize content
```js
editor.on('BeforeSetContent', function(e) {
  var sanitizedContent = ...; // Manually sanitize content here
  e.content = sanitizedContent;
});
```

### Acknowledgements
Tiny Technologies would like to thank Michał Bentkowski for discovering this vulnerability.

### References
https://www.tiny.cloud/docs/release-notes/release-notes514/#securityfixes

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [TinyMCE repo](https://github.com/tinymce/tinymce/issues)
* Email us at [infosec@tiny.cloud](mailto:infosec@tiny.cloud)

## References
- https://github.com/tinymce/tinymce/security/advisories/GHSA-27gm-ghr9-4v95
- https://nvd.nist.gov/vuln/detail/CVE-2020-17480
- https://github.com/tinymce/tinymce
- https://portswigger.net/daily-swig/xss-vulnerability-patched-in-tinymce
- https://www.tiny.cloud/docs/release-notes/release-notes514/#securityfixes
