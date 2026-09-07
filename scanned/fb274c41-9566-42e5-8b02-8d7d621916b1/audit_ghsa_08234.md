# [M] Kimai has an arbitrary file read in its invoice PDF renderer (admin)

## Summary
Severity: Medium
Advisory: GHSA-h5fh-7hwr-97mw
CVE: CVE-2026-44298
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-h5fh-7hwr-97mw
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=2.32.0 <2.56

## Details
## Summary

Users with the role `System-Admin` (`ROLE_SYSTE_ADMIN`) and the permission `upload_invoice_template` can upload PDF invoice templates, which can call `pdfContext.setOption('associated_files', ...)` inside the sandboxed Twig render. 

This is forwarded to mPDF's `SetAssociatedFiles()`, whose writer calls `file_get_contents($entry['path'])` during PDF output and embeds the bytes as a FlateDecode stream in the PDF. Any file readable by the PHP worker is returned to the attacker inside the rendered invoice.

## Root cause

1. `src/Twig/SecurityPolicy/StrictPolicy.php:123-128` explicitly whitelists `PdfContext::setOption()`:
   ```php
   if ($obj instanceof PdfContext) {
       if ($lcm !== 'setoption') { throw ...; }
       return;
   }
   ```

2. `src/Pdf/MPdfConverter.php` keeps `associated_files` in the pass-through allowlist:
   ```php
   $allowed = ['mode','format','default_font_size','default_font', ... , 'associated_files','additional_xmp_rdf'];
   ```
   and then forwards it to mPDF:
   ```php
   if (array_key_exists('associated_files', $options) && is_array($options['associated_files'])) {
       $associatedFiles = $options['associated_files'];
       unset($options['associated_files']);
   }
   ...
   $mpdf->SetAssociatedFiles($associatedFiles);
   ```

3. mPDF 8.3.1 `MetadataWriter::writeAssociatedFiles()` calls `file_get_contents`, which respects PHP stream wrappers:
   ```php
   if (isset($file['path'])) {
       $fileContent = @file_get_contents($file['path']);
   }
   ...
   $filestream = gzcompress($fileContent);
   $this->writer->write('<</Type /EmbeddedFile');
   ```

The sandbox and the option allowlist were both written defensively (short whitelists, not blacklists), but neither side considered that `associated_files` is a PDF/A file-embedding feature whose `path` key is a sink.

## Fix

The implemented fix has two aspects:

1. The `PdfContext` now works with a strict allow-list, that excludes `associated_files`
2. The `MPdfConverter` now removes any `path` from the `$associatedFiles` array, which can still be used by plugins:
```php
        if (\count($associatedFiles) > 0) {
            // remove "path" so mPDF will not use file_get_contents() on local files
            // callers must pre-read and pass the bytes via "content"
            $associatedFiles = array_map(static function ($entry): array {
                if (!\is_array($entry)) {
                    return [];
                }

                if (\array_key_exists('path', $entry)) {
                    unset($entry['path']);
                }

                return $entry;
            }, $associatedFiles);
            $mpdf->SetAssociatedFiles($associatedFiles);
        }

```

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-h5fh-7hwr-97mw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44298
- https://github.com/kimai/kimai
- https://github.com/kimai/kimai/releases/tag/2.56.0
