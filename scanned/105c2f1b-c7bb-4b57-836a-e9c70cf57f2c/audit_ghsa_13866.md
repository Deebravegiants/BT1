# [C] URI validation failure on SVG parsing. Bypass of CVE-2023-23924

## Summary
Severity: Critical
Advisory: GHSA-56gj-mvh6-rp75
CVE: CVE-2023-24813
CWE: CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-07
Source: https://github.com/advisories/GHSA-56gj-mvh6-rp75
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=2.0.2 <2.0.3

## Details
### Summary
Due to the difference in the attribute parser of Dompdf and php-svg-lib, an attacker can still call arbitrary URLs with arbitrary protocols.

### Details
Dompdf parses the href attribute of `image` tags with the following code:

[`src/Image/Cache.php` line 135-150](https://github.com/dompdf/dompdf/blob/2a8a6b80fcaa5148ace50f35a10979fe00c6a35d/src/Image/Cache.php#L135-L150)
``` php
function ($parser, $name, $attributes) use ($options, $parsed_url, $full_url) {
    if (strtolower($name) === "image") {
        $attributes = array_change_key_case($attributes, CASE_LOWER);
        $url = $attributes["xlink:href"] ?? $attributes["href"];
        if (!empty($url)) {
            $inner_full_url = Helpers::build_url($parsed_url["protocol"], $parsed_url["host"], $parsed_url["path"], $url);
            if ($inner_full_url === $full_url) {
                throw new ImageException("SVG self-reference is not allowed", E_WARNING);
            }
            [$resolved_url, $type, $message] = self::resolve_url($url, $parsed_url["protocol"], $parsed_url["host"], $parsed_url["path"], $options);
            if (!empty($message)) {
                throw new ImageException("This SVG document references a restricted resource. $message", E_WARNING);
            }
        }
    }
},
```

As you can see from the code snippet above, it respects `xlink:href` even if `href` is specified.
``` php
$url = $attributes["xlink:href"] ?? $attributes["href"];
```

However, php-svg-lib, which is later used to parse the svg file, parses the href attribute with the following code:

[`src/Svg/Tag/Image.php` line 51-57](https://github.com/dompdf/php-svg-lib/blob/76876c6cf3080bcb6f249d7d59705108166a6685/src/Svg/Tag/Image.php#L51-L57)
``` php
if (isset($attributes['xlink:href'])) {
    $this->href = $attributes['xlink:href'];
}

if (isset($attributes['href'])) {
    $this->href = $attributes['href'];
}
```

Since `href` is respected if both `xlink:href` and `href` is specified, it's possible to bypass the protection on the Dompdf side by providing an empty `xlink:href` attribute.

### Impact
An attacker can exploit the vulnerability to call arbitrary URLs with arbitrary protocols if they provide an SVG file to the Dompdf. In PHP versions before 8.0.0, it leads to arbitrary unserialize, which will lead, at the very least, to arbitrary file deletion and might lead to remote code execution, depending on available classes.

## References
- https://github.com/dompdf/dompdf/security/advisories/GHSA-56gj-mvh6-rp75
- https://nvd.nist.gov/vuln/detail/CVE-2023-24813
- https://github.com/dompdf/dompdf/commit/95009ea98230f9b084b040c34e3869ef3dccc9aa
- https://github.com/dompdf/dompdf
