# [H] PhpSpreadsheet allows unauthorized Reflected XSS in the constructor of the Downloader class

## Summary
Severity: High
Advisory: GHSA-jmpx-686v-c3wx
CVE: CVE-2024-56365
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-01-03
Source: https://github.com/advisories/GHSA-jmpx-686v-c3wx
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.0.0 <3.7.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.6
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.5
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
# Unauthorized Reflected XSS in the constructor of the `Downloader` class

**Product**: Phpspreadsheet
**Version**: version 3.6.0
**CWE-ID**: CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
**CVSS vector v.3.1**: 8.2 (AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)
**CVSS vector v.4.0**: 8.3 (AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:L/SI:H/SA:L)
**Description**: using the `/vendor/phpoffice/phpspreadsheet/samples/download.php` script, an attacker can perform a XSS-type attack
**Impact**: execution of arbitrary JavaScript code in the browser
**Vulnerable component**: the constructor of the `Downloader` class
**Exploitation conditions**: an unauthorized user
**Mitigation**: sanitization of the `name` and `type` variables
**Researcher**: Aleksey Solovev (Positive Technologies)

# Research

The researcher discovered zero-day vulnerability Unauthorized Reflected Cross-Site Scripting (XSS) (in the constructor of the `Downloader` class) in Phpspreadsheet.

The latest version (3.6.0) of the `phpoffice/phpspreadsheet` library was installed. The installation was carried out with the inclusion of examples.

*Listing 1. Installing the `phpoffice/phpspreadsheet` library*
```
$ composer require phpoffice/phpspreadsheet --prefer-source
```

The `./vendor/phpoffice/phpspreadsheet/samples/download.php` file processes the GET parameters `name` and `type`.

![fig1](https://github.com/user-attachments/assets/78d5b3c7-e2ab-4487-98e2-a975f74a71c0)

*Figure 1. The `./vendor/phpoffice/phpspreadsheet/samples/download.php` file accepts GET parameters.*

Consider the constructor of the `Downloader` class, where GET parameters are passed. Error is displayed without sanitization using GET parameters transmitted from the user.

![fig2](https://github.com/user-attachments/assets/00baf1f8-298c-4654-a3e4-b99cf8053eac)

*Figure 2. Error is displayed without sanitization*

When clicking on the following link, arbitrary JavaScript code will be executed.

*Listing 2.*
```
https://192.***.***.***/vendor/phpoffice/phpspreadsheet/samples/download.php?name=%3Cimg%20src=1%20onerror=alert()%3E&type=1
```

Demonstration of the execution of arbitrary JavaScript code.

<img width="537" alt="fig3" src="https://github.com/user-attachments/assets/745d6e21-396f-4357-8ff8-e856adf15fee" />

*Figure 3. Executing arbitrary JavaScript code*


# Credit
This vulnerability was discovered by **Aleksey Solovev (Positive Technologies)**

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-jmpx-686v-c3wx
- https://nvd.nist.gov/vuln/detail/CVE-2024-56365
- https://github.com/PHPOffice/PhpSpreadsheet/commit/700a80346be269af668914172bc6f4521982d0b4#diff-fbb0f53a5c68eeeffaa9ab35552c0b01740396f1a4045af5d2935ec2a62a7816
- https://github.com/PHPOffice/PhpSpreadsheet
