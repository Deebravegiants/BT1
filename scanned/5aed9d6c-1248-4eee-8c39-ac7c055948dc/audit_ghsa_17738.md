# [M] Cross-Site Scripting (XSS) vulnerability in generateNavigation() function in PhpSpreadsheet

## Summary
Severity: Medium
Advisory: GHSA-79xx-vf93-p7cx
CVE: CVE-2025-22131
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-79xx-vf93-p7cx
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.0.0 <3.8.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.8
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.6
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
### Summary
The researcher discovered zero-day vulnerability Cross-Site Scripting (XSS) vulnerability in the code which translates the XLSX file into a HTML representation and displays it in the response.

### Details
When generating the HTML from an xlsx file containing multiple sheets, a navigation menu is created. This menu includes the sheet names, which are not sanitized. As a result, an attacker can exploit this vulnerability to execute JavaScript code.

```php
        // Construct HTML
        $html = '';

        // Only if there are more than 1 sheets
        if (count($sheets) > 1) {
            // Loop all sheets
            $sheetId = 0;

            $html .= '<ul class="navigation">' . PHP_EOL;

            foreach ($sheets as $sheet) {
                $html .= '  <li class="sheet' . $sheetId . '"><a href="#sheet' . $sheetId . '">' . $sheet->getTitle() . '</a></li>' . PHP_EOL;
                ++$sheetId;
            }

            $html .= '</ul>' . PHP_EOL;
        }
```

### PoC
1. Create an XLSX file with multiple sheets : 
![image](https://github.com/user-attachments/assets/e3fc027a-9525-4d7f-b107-cfa6e78d04e7)

2. Generate the HTML content 
```php
<?php
	require __DIR__ . '/vendor/autoload.php';

	$inputFileName = 'payload.xlsx';
	$spreadsheet = \PhpOffice\PhpSpreadsheet\IOFactory::load($inputFileName);
	$writer = new \PhpOffice\PhpSpreadsheet\Writer\Html($spreadsheet);
	$writer->writeAllSheets();
	echo $writer->generateHTMLAll();
?>
```
3. Enjoy
![image](https://github.com/user-attachments/assets/3e3c24f4-cb5d-451d-978f-9d33234f3bd1)


### Impact

XSS can cause a variety of problems for the end user that range in severity from an annoyance to complete account compromise.
Example of impacts :

- Disclosure of the user’s session cookie, allowing an attacker to hijack the user’s session and take over the account (Only if HttpOnly cookie's flag is set to false).
- Redirecting the user to some other page or site (like phishing websites)
- Modifying the content of the current page (add a fake login page that sends credentials to the attacker).
- Automatically download malicious files.
- Requests access to the victim geolocation / camera.
- ...

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-79xx-vf93-p7cx
- https://nvd.nist.gov/vuln/detail/CVE-2025-22131
- https://github.com/PHPOffice/PhpSpreadsheet/commit/4088381ccfaf241d7d42c333de0dc8c98e338743
- https://github.com/PHPOffice/PhpSpreadsheet
