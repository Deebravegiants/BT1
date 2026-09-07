# [M] Stored Cross-site Scripting (XSS) in excalidraw's web embed component

## Summary
Severity: Medium
Advisory: GHSA-m64q-4jqh-f72f
CVE: CVE-2024-32472
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-m64q-4jqh-f72f
Type: github-advisory

## Affected
- npm: `@excalidraw/excalidraw` — affected >=0.16.0 <0.16.4
- npm: `@excalidraw/excalidraw` — affected >=0.17.0 <0.17.6

## Details
### Summary

A stored XSS vulnerability in Excalidraw's web embeddable component. This allows arbitrary JavaScript to be run in the context of the domain where the editor is hosted. 

### Poc

Inserting an embed with the below url (can be copy/pasted onto canvas to insert as embed) will log `42` to the console:

```
https://gist.github.com/vv=v<script>console.log(42)</script>
```

### Details

There were two vectors. One rendering untrusted string as iframe's `srcdoc` without properly sanitizing against HTML injection. Second by improperly sanitizing against attribute HTML injection. This in conjunction with allowing `allow-same-origin` sandbox flag (necessary for several embeds) resulted in the XSS.

Former was fixed by no longer rendering unsafe `srcdoc` content verbatim, and instead strictly parsing the supplied content and constructing the `srcdoc` manually. The latter by sanitizing properly.

The `allow-same-origin` flag is now also set only in cases that require it, following the principle of least privilege.

### Impact

This is a cross site scripting vulnerability, for more information, please see: https://portswigger.net/web-security/cross-site-scripting

Two npm `@excalidraw/excalidraw` stable version releases were affected (`0.16.x`, `0.17.x`), and both are now patched.

## References
- https://github.com/excalidraw/excalidraw/security/advisories/GHSA-m64q-4jqh-f72f
- https://nvd.nist.gov/vuln/detail/CVE-2024-32472
- https://github.com/excalidraw/excalidraw/commit/6be752e1b6d776ccfbd3bb9eea17463cb264121d
- https://github.com/excalidraw/excalidraw/commit/988f81911ca58e3ca2583e0dd44a954dd00e09d0
- https://github.com/excalidraw/excalidraw
