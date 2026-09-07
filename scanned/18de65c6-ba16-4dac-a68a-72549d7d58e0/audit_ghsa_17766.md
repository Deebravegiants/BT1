# [M] PhpSpreadsheet has a Cross-Site Scripting (XSS) vulnerability of the hyperlink base in the HTML page header

## Summary
Severity: Medium
Advisory: GHSA-hwcp-2h35-p66w
CVE: CVE-2024-56411
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-03
Source: https://github.com/advisories/GHSA-hwcp-2h35-p66w
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.0.0 <3.7.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.6
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.5
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
# Cross-Site Scripting (XSS) vulnerability of the hyperlink base in the HTML page header

**Product**: Phpspreadsheet
**Version**: version 3.6.0
**CWE-ID**: CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
**CVSS vector v.3.1**: 5.4 (AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
**CVSS vector v.4.0**: 4.8 (AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N)
**Description**: the HTML page is formed without sanitizing the hyperlink base
**Impact**: executing arbitrary JavaScript code in the browser
**Vulnerable component**: class `PhpOffice\PhpSpreadsheet\Writer\Html`, method `generateHTMLHeader`
**Exploitation conditions**: a user viewing a specially generated Excel file
**Mitigation**: additional sanitization of special characters in a string
**Researcher**: Aleksey Solovev (Positive Technologies)

# Research

The researcher discovered zero-day vulnerability Cross-Site Scripting (XSS) vulnerability of the hyperlink base in the HTML page header in Phpspreadsheet.
The following code is written on the server, which translates the XLSX file into a HTML representation and displays it in the response.

*Listing 8. Source code on the server*

```
<?php

require __DIR__ . '/vendor/autoload.php';

$inputFileName = './doc/Book1.xlsx';
$spreadsheet = \PhpOffice\PhpSpreadsheet\IOFactory::load($inputFileName);
$writer = new \PhpOffice\PhpSpreadsheet\Writer\Html($spreadsheet);
print($writer->generateHTMLAll());
```

An attacker can embed a payload in a file property that will result in the execution of arbitrary JavaScript code.
The Excel file is unpacked and a HyperlinkBase in the file is inserted into the `docProps/app.xml` file.

![fig14](https://github.com/user-attachments/assets/f68ef7fc-e78e-4424-8753-4318b6ff51c3)

*Figure 14. Embedding the payload* 

After the changes were made, a new archive with the xlsx extension was created. At the moment of converting the xlsx file into the HTML representation, a property is obtained that participates in the formation of a string without sanitization.

![fig15](https://github.com/user-attachments/assets/0aa7398c-ddd9-4c5a-ab04-41af0236dcba)

*Figure 15. Generating the HTML page header using the HyperlinkBase property* 

After generating and displaying the HTML representation of the XLSX file, arbitrary JavaScript code will be executed.
<img width="356" alt="fig16" src="https://github.com/user-attachments/assets/c3694661-31e3-4be8-9a86-6eb4dd4647b5" />

*Figure 16. Executing arbitrary JavaScript code* 

# Credit
This vulnerability was discovered by **Aleksey Solovev (Positive Technologies)**

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-hwcp-2h35-p66w
- https://nvd.nist.gov/vuln/detail/CVE-2024-56411
- https://github.com/PHPOffice/PhpSpreadsheet/commit/45052f88e04c735d56457a8ffcdc40b2635a028e
- https://github.com/PHPOffice/PhpSpreadsheet
