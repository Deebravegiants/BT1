# [H] Kimai has an XXE Leading to Local File Read

## Summary
Severity: High
Advisory: GHSA-534c-hcr7-67jg
CWE: CWE-1395, CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-534c-hcr7-67jg
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.21.0

## Details
### Summary
Kimai uses [PHPSpreadsheet](https://github.com/PHPOffice/PhpSpreadsheet) for importing and exporting invoices. Recently, a [CVE](https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-ghg6-32f9-2jp7) was identified in PHPSpreadsheet, which could lead to an XXE vulnerability.


### Details

Exploitation requires an Administrator account, allowing the upload of an `XLSX` template containing the payload. The vulnerability is triggered by the following code snippet:

```php
// https://github.com/kimai/kimai/blob/b1903ba18359be16dd32ea9c40377c486498f082/src/Invoice/Renderer/AbstractSpreadsheetRenderer.php#L41
public function render(InvoiceDocument $document, InvoiceModel $model): Response
{
    $spreadsheet = IOFactory::load($document->getFilename());
    $worksheet = $spreadsheet->getActiveSheet();
    $entries = $model->getCalculator()->getEntries();
    $sheetReplacer = $model->toArray();
    $invoiceItemCount = \count($entries);
    if ($invoiceItemCount > 1) {
        $this->addTemplateRows($worksheet, $invoiceItemCount);
    }
}
```

The `IOFactory::load` function utilizes `simplexml_load_string`, which has previously been demonstrated to be vulnerable to XXE attacks.

While this is not directly an XXE in Kimai, it does however impact the latest stable version.

 
### PoC

By uploading a malicious `XLSX` template, the payload will be triggered every time an invoice is generated.

```xml
<?xml version="1.0" encoding='UTF-7' standalone="yes"?>
+ADw-!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "php://filter/......." > %xxe;]>.....
```

For a better a visibility, I will upload both a:
- Malicious template sample for testing 
- An exported invoice, showing the contents of target file during the export. 

### Impact
Local File Read / RCE in edge cases where `phar://` can be utilized with [gadget chains](https://github.com/ambionics/phpggc) . 


[export.xlsx](https://github.com/user-attachments/files/16803913/export.xlsx)
[sample_template.xlsx](https://github.com/user-attachments/files/16803916/sample_template.xlsx)

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-ghg6-32f9-2jp7
- https://github.com/kimai/kimai/security/advisories/GHSA-534c-hcr7-67jg
- https://github.com/kimai/kimai/commit/3204dcb03e1003dba90178667a4667ce3edb87b5
- https://github.com/kimai/kimai
