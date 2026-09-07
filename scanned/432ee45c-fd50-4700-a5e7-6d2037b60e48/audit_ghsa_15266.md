# [M] PhpSpreadsheet HTML writer is vulnerable to Cross-Site Scripting via style information

## Summary
Severity: Medium
Advisory: GHSA-wgmf-q9vr-vww6
CVE: CVE-2024-45046
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-wgmf-q9vr-vww6
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.1
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
### Summary

`\PhpOffice\PhpSpreadsheet\Writer\Html` doesn't sanitize spreadsheet styling information such as font names, allowing an attacker to inject arbitrary JavaScript on the page.

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
[book.xlsx](https://github.com/PHPOffice/PhpSpreadsheet/files/15212797/book.xlsx)

Open index.php in a web browser. An alert should be displayed.

### Impact

Full takeover of the session of users viewing spreadsheet files as HTML.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-wgmf-q9vr-vww6
- https://nvd.nist.gov/vuln/detail/CVE-2024-45046
- https://github.com/PHPOffice/PhpSpreadsheet/pull/3957
- https://github.com/PHPOffice/PhpSpreadsheet/commit/f7cf378faed2e11cf4825bf8bafea4922ae44667
- https://github.com/PHPOffice/PhpSpreadsheet
