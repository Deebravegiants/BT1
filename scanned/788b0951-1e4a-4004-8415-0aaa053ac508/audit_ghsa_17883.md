# [H] PhpSpreadsheet vulnerable to SSRF when reading and displaying a processed HTML document in the browser

## Summary
Severity: High
Advisory: GHSA-rx7m-68vc-ppxh
CVE: CVE-2025-54370
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-25
Source: https://github.com/advisories/GHSA-rx7m-68vc-ppxh
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.12
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.0.0 <3.10.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.0.0

## Details
**Product:** PhpSpreadsheet
**Version:** 3.8.0
**CWE-ID:** CWE-918: Server-Side Request Forgery (SSRF)
**CVSS vector v.3.1:** 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
**CVSS vector v.4.0:** 8.7 (AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
**Description:** SSRF occurs when a processed HTML document is read and displayed in the browser
**Impact:** Server-Side Request Forgery
**Vulnerable component:** the `PhpOffice\PhpSpreadsheet\Worksheet\Drawing` class, `setPath` method
**Exploitation conditions:** getting a string from the user that is passed to the HTML reader
**Mitigation:** improved processing of the `$path` variable of the `setPath` method of the `PhpOffice\PhpSpreadsheet\Worksheet\Drawing` class is needed
**Researcher: Aleksey Solovev (Positive Technologies)**

# Research
The researcher discovered zero-day vulnerability Server-Side Request Forgery (SSRF) (in the `setPath` method of the `PhpOffice\PhpSpreadsheet\Worksheet\Drawing` class) in Phpspreadsheet.
The latest version (3.8.0) of the `phpoffice/phpspreadsheet` library was installed. Below are the details of the installation:

*Listing 1. Installing the phpoffice/phpspreadsheet library*
```
$ composer require phpoffice/phpspreadsheet --prefer-source
```
The code that processes the HTML string with further rendering and displaying the result in the browser.
*Listing 2. Executable file index.php using the PhpSpreadsheet library*
```
<?php

require __DIR__ . '/vendor/autoload.php';

$inputFileType = 'Html';
$reader = \PhpOffice\PhpSpreadsheet\IOFactory::createReader($inputFileType);  


$inputFileName = './doc/file.html';
$spreadsheet = $reader->load($inputFileName); 

$writer = new \PhpOffice\PhpSpreadsheet\Writer\Html($spreadsheet); 
print($writer->generateHTMLAll());
```

Also, the `./doc/file.html` has the following content: the `img` tag with the `src` attribute, which contains the value `http:// 127.0.0.1:1337`

*Listing 3. The ./doc/file.html file*
```
<table>
    <tr>
        <img src="http://127.0.0.1:1337">
    </tr>
</table>
```
The vulnerability lies in the `setPath` method of the `PhpOffice\PhpSpreadsheet\Worksheet\Drawing` class.
 
Figure 1. The `PhpOffice\PhpSpreadsheet\Worksheet\Drawing` class, `setPath` method.

![fig1](https://github.com/user-attachments/assets/75433f59-fac6-46d5-bcfd-6d0174bfcedd)

Figure 2 below demonstrates the SSRF vulnerability exploitation.

![fig2](https://github.com/user-attachments/assets/3601692b-b077-420f-a2fb-8af0b66b6475)

Figure 2. Demonstration of the SSRF vulnerability exploitation

Also, there is code on line 154 that could potentially be used by an attacker to perform unsafe deserialization via the `phar` archive and the `file_exists` method.
 
Figure 3. Opportunity to perform phar deserialization
![fig3](https://github.com/user-attachments/assets/3d7d4fc2-1b89-4925-82fa-e21c773efd47)

_____________________________________________

Please, assign all credits to: Aleksey Solovev (Positive Technologies)

# Credit

Aleksey Solovev (Positive Technologies)

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-rx7m-68vc-ppxh
- https://nvd.nist.gov/vuln/detail/CVE-2025-54370
- https://github.com/PHPOffice/PhpSpreadsheet/commit/334a67797ace574d1d37c0992ffe283b7415471a
- https://github.com/PHPOffice/PhpSpreadsheet/commit/4050f14521d70634c3320b170236574a6106eb39
- https://github.com/PHPOffice/PhpSpreadsheet/commit/81a0de2261f698404587a6421a5c6eb263c40b31
- https://github.com/PHPOffice/PhpSpreadsheet/commit/ac4befd2f7ccc21a59daef606a02a3d1828ade09
- https://github.com/PHPOffice/PhpSpreadsheet/commit/c2cd0e64392438e4c6af082796eb65c1d629a266
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpoffice/phpspreadsheet/CVE-2025-54370.yaml
- https://github.com/PHPOffice/PhpSpreadsheet
