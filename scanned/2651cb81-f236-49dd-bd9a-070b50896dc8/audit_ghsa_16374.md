# [M] php-svg-lib lacks path validation on font through SVG inline styles 

## Summary
Severity: Medium
Advisory: GHSA-f3qr-qr4x-j273
CVE: CVE-2024-25117
CWE: CWE-502, CWE-610, CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-f3qr-qr4x-j273
Type: github-advisory

## Affected
- Packagist: `phenx/php-svg-lib` — affected >=0 <0.5.2

## Details
### Summary
php-svg-lib fails to validate that font-family doesn't contain a PHAR url, which might leads to RCE on PHP < 8.0, and doesn't validate if external references are allowed. This might leads to bypass of restrictions or RCE on projects that are using it, if they do not strictly revalidate the fontName that is passed by php-svg-lib.

### Details
The Style::fromAttributes(), or the Style::parseCssStyle() should check the content of the `font-family` and prevents it to use a PHAR url, to avoid passing an invalid and dangerous `fontName` value to other libraries. The same check as done in the Style::fromStyleSheets might be reused : 

```
                if (
                    \array_key_exists("font-family", $styles)
                    && (
                        \strtolower(\substr($this->href, 0, 7)) === "phar://"
                        || ($this->document->allowExternalReferences === false && \strtolower(\substr($this->href, 0, 5)) !== "data:")
                    )
                ) {
                    unset($style["font-family"]);
                }
```

### PoC 

Parsing the following SVG : 

```
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200">
    <text x="20" y="35" style="color:red;font-family:phar:///path/to/whatever.phar/blaklis;">My</text>
</svg>
```

will pass the `phar:///path/to/whatever.phar/blaklis` as `$family` in `SurfaceCpdf::setFont`, which is then passed to the canvas `selectFont` as a `$fontName`.

### Impact
Libraries using this library as a dependency might be vulnerable to some bypass of restrictions, or even RCE, if they do not double check the value of the `fontName` that is passed by php-svg-lib

## References
- https://github.com/dompdf/php-svg-lib/security/advisories/GHSA-f3qr-qr4x-j273
- https://nvd.nist.gov/vuln/detail/CVE-2024-25117
- https://github.com/dompdf/php-svg-lib/commit/732faa9fb4309221e2bd9b2fda5de44f947133aa
- https://github.com/dompdf/php-svg-lib/commit/8ffcc41bbde39f09f94b9760768086f12bbdce42
- https://github.com/dompdf/php-svg-lib
