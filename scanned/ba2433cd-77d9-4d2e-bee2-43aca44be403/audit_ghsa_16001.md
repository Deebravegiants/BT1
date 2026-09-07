# [M] PhpSpreadsheet HTML writer is vulnerable to Cross-Site Scripting via JavaScript hyperlinks

## Summary
Severity: Medium
Advisory: GHSA-r8w8-74ww-j4wh
CVE: CVE-2024-45292
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-07
Source: https://github.com/advisories/GHSA-r8w8-74ww-j4wh
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.2
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.1
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
### Summary
`\PhpOffice\PhpSpreadsheet\Writer\Html` does not sanitize "javascript:" URLs from hyperlink `href` attributes, resulting in a Cross-Site Scripting vulnerability.

### PoC

Example target script:

```
<?php

require 'vendor/autoload.php';

$reader = \PhpOffice\PhpSpreadsheet\IOFactory::createReader("Xlsx");
$spreadsheet = $reader->load(__DIR__ . '/book.xlsx');

$writer = new \PhpOffice\PhpSpreadsheet\Writer\Html($spreadsheet);
print($writer->generateHTMLAll());
```

Save this file in the same directory:
[book.xlsx](https://github.com/PHPOffice/PhpSpreadsheet/files/15099763/book.xlsx)

Open index.php in a web browser and click on both links. The first demonstrates the vulnerability in a regular hyperlink and the second in a HYPERLINK() formula.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-r8w8-74ww-j4wh
- https://nvd.nist.gov/vuln/detail/CVE-2024-45292
- https://github.com/PHPOffice/PhpSpreadsheet/commit/392dd08c5569b623060784e1333454d64df1f03d
- https://github.com/PHPOffice/PhpSpreadsheet/commit/8b9b378ecdc603234a34aab3b293d2cdc8e9210e
- https://github.com/PHPOffice/PhpSpreadsheet/commit/f0b70ed1086348904b27772b264e1605ba6c1d6d
- https://github.com/PHPOffice/PhpSpreadsheet
