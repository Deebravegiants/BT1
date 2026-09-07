# [M] PhpSpreadsheet allows bypass XSS sanitizer using the javascript protocol and special characters

## Summary
Severity: Medium
Advisory: GHSA-q9jv-mm3r-j47r
CVE: CVE-2024-56412
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-03
Source: https://github.com/advisories/GHSA-q9jv-mm3r-j47r
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.0.0 <3.7.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.6
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.5
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
# Bypass XSS sanitizer using the javascript protocol and special characters

**Product**: Phpspreadsheet
**Version**: version 3.6.0
**CWE-ID**: CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
**CVSS vector v.3.1**: 5.4 (AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
**CVSS vector v.4.0**: 4.8 (AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N)
**Description**: an attacker can use special characters, so that the library processes the javascript protocol with special characters and generates an HTML link
**Impact**: executing arbitrary JavaScript code in the browser
**Vulnerable component**: class `PhpOffice\PhpSpreadsheet\Writer\Html`, method `generateRow`
**Exploitation conditions**: a user viewing a specially generated Excel file
**Mitigation**: additional sanitization of special characters in a string
**Researcher**: Aleksey Solovev (Positive Technologies)

# Research

The researcher discovered zero-day vulnerability Bypass XSS sanitizer using the javascript protocol and special characters in Phpspreadsheet.

The following code is written on the server, which translates the XLSX file into a HTML representation and displays it in the response.

*Listing 6. Source code on the server*

```
<?php

require __DIR__ . '/vendor/autoload.php';

$inputFileName = './doc/Book1.xlsx';
$spreadsheet = \PhpOffice\PhpSpreadsheet\IOFactory::load($inputFileName);
$writer = new \PhpOffice\PhpSpreadsheet\Writer\Html($spreadsheet);
print($writer->generateHTMLAll());
```

An attacker can use special characters so that this library processes the javascript protocol with special characters and generates a HTML link.
The Excel file is unpacked and a hyperlink in the file is inserted into the `xl/worksheets/sheet1.xml` file.

![fig11](https://github.com/user-attachments/assets/b9d53f7a-6f36-4853-95f9-8aa22f81eccd)

*Figure 11. Using the javascript protocol with special characters*

Some payloads help bypass the security system and carry out a XSS attack.

*Listing 7. HTML form that demonstrates the exploitation of the XSS vulnerability*

```
jav&#x09;ascript:alert()
jav&#x0D;ascript:alert()
jav&#x0A;ascript:alert()
```

It's clear that the javascript protocol with special characters is used. 

![fig12](https://github.com/user-attachments/assets/7595e88b-9848-4251-845c-2c2d8032e479)

*Figure 12. Using the javascript protocol with special characters*

Due to the special characters, the execution stream ends up on line 1543, and the link is built in HTML form with the javascript protocol.

<img width="373" alt="fig13" src="https://github.com/user-attachments/assets/3ca0c3c6-daa9-4502-ad9e-b803f308fd26" />

*Figure 13. Executing arbitrary JavaScript code*

# Credit
This vulnerability was discovered by **Aleksey Solovev (Positive Technologies)**

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-q9jv-mm3r-j47r
- https://nvd.nist.gov/vuln/detail/CVE-2024-56412
- https://github.com/PHPOffice/PhpSpreadsheet/commit/45052f88e04c735d56457a8ffcdc40b2635a028e
- https://github.com/PHPOffice/PhpSpreadsheet
