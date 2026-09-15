# [C] Dompdf vulnerable to URI validation failure on SVG parsing

## Summary
Severity: Critical
Advisory: GHSA-3cw5-7cxw-v5qg
CVE: CVE-2023-23924
CWE: CWE-551, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:H (CVSS_V3)
Published: 2023-02-01
Source: https://github.com/advisories/GHSA-3cw5-7cxw-v5qg
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <2.0.2

## Details
### Summary
The URI validation on dompdf 2.0.1 can be bypassed on SVG parsing by passing `<image>` tags with uppercase letters. This might leads to arbitrary object unserialize on PHP < 8, through the `phar` URL wrapper.

### Details
The bug occurs during SVG parsing of `<image>` tags, in src/Image/Cache.php : 

```
if ($type === "svg") {
    $parser = xml_parser_create("utf-8");
    xml_parser_set_option($parser, XML_OPTION_CASE_FOLDING, false);
    xml_set_element_handler(
        $parser,
        function ($parser, $name, $attributes) use ($options, $parsed_url, $full_url) {
            if ($name === "image") {
                $attributes = array_change_key_case($attributes, CASE_LOWER);
```
This part will try to detect `<image>` tags in SVG, and will take the href to validate it against the protocolAllowed whitelist. However, the `$name comparison with "image" is case sensitive, which means that such a tag in the SVG will pass : 

```
<svg>
    <Image xlink:href="phar:///foo"></Image>
</svg>
```

As the tag is named "Image" and not "image", it will not pass the condition to trigger the check.

A correct solution would be to strtolower the `$name` before the check : 

```
if (strtolower($name) === "image") {
```

### PoC
Parsing the following SVG file is sufficient to reproduce the vulnerability :

```
<svg>
    <Image xlink:href="phar:///foo"></Image>
</svg>
```

### Impact
An attacker might be able to exploit the vulnerability to call arbitrary URL with arbitrary protocols, if they can provide a SVG file to dompdf. In PHP versions before 8.0.0, it leads to arbitrary unserialize, that will leads at the very least to an arbitrary file deletion, and might leads to remote code execution, depending on classes that are available.

## References
- https://github.com/dompdf/dompdf/security/advisories/GHSA-3cw5-7cxw-v5qg
- https://nvd.nist.gov/vuln/detail/CVE-2023-23924
- https://github.com/dompdf/dompdf/commit/7558f07f693b2ac3266089f21051e6b78c6a0c85
- https://github.com/FriendsOfPHP/security-advisories/blob/master/dompdf/dompdf/CVE-2023-23924.yaml
- https://github.com/advisories/GHSA-3cw5-7cxw-v5qg
- https://github.com/dompdf/dompdf
- https://github.com/dompdf/dompdf/releases/tag/v2.0.2
