# [M] PhpSpreadsheet has a Cross-Site Scripting (XSS) vulnerability in custom properties

## Summary
Severity: Medium
Advisory: GHSA-wv23-996v-q229
CVE: CVE-2024-56410
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-03
Source: https://github.com/advisories/GHSA-wv23-996v-q229
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.0.0 <3.7.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.6
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.5
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
# Cross-Site Scripting (XSS) vulnerability in custom properties

**Product**: Phpspreadsheet
**Version**: version 3.6.0
**CWE-ID**: CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
**CVSS vector v.3.1**: 5.4 (AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
**CVSS vector v.4.0**: 4.8 (AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N)
**Description**: the HTML page is generated without clearing custom properties
**Impact**: executing arbitrary JavaScript code in the browser
**Vulnerable component**: class `PhpOffice\PhpSpreadsheet\Writer\Html`, method `generateMeta`
**Exploitation conditions**: a user viewing a specially generated Excel file
**Mitigation**: additional sanitization of special characters in a string
**Researcher**: Aleksey Solovev (Positive Technologies)

# Research

The researcher discovered zero-day vulnerability Cross-Site Scripting (XSS) vulnerability in custom properties in Phpspreadsheet.
The following code is written on the server, which translates the XLSX file into a HTML representation and displays it in the response.

*Listing 9. Source code on the server*

```
<?php

require __DIR__ . '/vendor/autoload.php';

$inputFileName = './doc/Book1.xlsx';
$spreadsheet = \PhpOffice\PhpSpreadsheet\IOFactory::load($inputFileName);
$writer = new \PhpOffice\PhpSpreadsheet\Writer\Html($spreadsheet);
print($writer->generateHTMLAll());
```

An attacker can embed a payload in a file property that will result in the execution of arbitrary JavaScript code.
The Excel file is unpacked and a custom property in the file is inserted into the `docProps/custom.xml` file.

![fig17](https://github.com/user-attachments/assets/65453b48-bca5-4f5c-a683-315a7bb1ab1f)

*Figure 17. Embedding the payload*

After making the changes, a new archive with the xlsx extension was created. At the moment of converting the xlsx file into an HTML representation, a property is obtained that participates in the formation of a string without sanitization.

![fig18](https://github.com/user-attachments/assets/e0f63bfb-d9e1-4c9d-a2a9-8a0a20406cdc)

*Figure 18. Getting a custom property*

When calling the static `generateMeta` method, you can see that the key of the custom property is displayed without sanitization.

![fig19](https://github.com/user-attachments/assets/8c74e264-af68-4f62-8ac7-437e65884e86)

*Figure 19. Getting a custom property*

As a result, when viewing the excel file as the HTML representation, arbitrary JavaScript code will be executed.

<img width="356" alt="fig20" src="https://github.com/user-attachments/assets/a6ed21e3-685c-415c-b2dc-453bc0652bef" />

*Figure 20. Executing arbitrary JavaScript code*

# Credit
This vulnerability was discovered by **Aleksey Solovev (Positive Technologies)**

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-wv23-996v-q229
- https://nvd.nist.gov/vuln/detail/CVE-2024-56410
- https://github.com/PHPOffice/PhpSpreadsheet/commit/45052f88e04c735d56457a8ffcdc40b2635a028e
- https://github.com/PHPOffice/PhpSpreadsheet
