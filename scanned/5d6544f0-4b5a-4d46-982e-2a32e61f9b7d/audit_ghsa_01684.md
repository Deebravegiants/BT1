# [M] XSS in TinyMCE

## Summary
Severity: Medium
Advisory: GHSA-c78w-2gw7-gjv3
CVE: CVE-2019-1010091
CWE: CWE-79
Ecosystem: npm
Published: 2020-05-11
Source: https://github.com/advisories/GHSA-c78w-2gw7-gjv3
Type: github-advisory

## Affected
- npm: `tinymce` — affected >=0 <4.9.10
- npm: `tinymce` — affected >=5.0.0 <5.2.2

## Details
### Impact
A cross-site scripting (XSS) vulnerability was discovered in: the core parser and `media` plugin. The vulnerability allowed arbitrary JavaScript execution when inserting a specially crafted piece of content into the editor via the clipboard or APIs. This impacts all users who are using TinyMCE 4.9.9 or lower and TinyMCE 5.2.1 or lower.

### Patches
This vulnerability has been patched in TinyMCE 4.9.10 and 5.2.2 by improved HTML parsing and sanitization logic.

### Workarounds
The workarounds available are:
- disable the media plugin and manually sanitize CDATA content (see below)
or
- upgrade to either TinyMCE 4.9.10 or TinyMCE 5.2.2

#### Example: Manually strip CDATA elements
```js
setup: function(editor) {
  editor.on('PreInit', function() {
    editor.parser.addNodeFilter('#cdata', function(nodes) {
      for (var i = 0; i < nodes.length; i++) {
        nodes[i].remove();
      }
    });
  });
}
```

### Acknowledgements
Tiny Technologies would like to thank Michał Bentkowski and [intivesec](https://github.com/intivesec) for discovering these vulnerabilities.

### References
https://www.tiny.cloud/docs/release-notes/release-notes522/#securityfixes

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [TinyMCE repo](https://github.com/tinymce/tinymce/issues)
* Email us at [infosec@tiny.cloud](mailto:infosec@tiny.cloud)

## References
- https://github.com/tinymce/tinymce/security/advisories/GHSA-c78w-2gw7-gjv3
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010091
- https://github.com/tinymce/tinymce/issues/4394
