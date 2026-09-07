# [M] Laravel Backpack CRUD: SingleBase64Image accepts any base64 payload behind a `data:image` prefix — SVG-with-script lands on the public disk

## Summary
Severity: Medium
Advisory: GHSA-8hw4-7qjr-3wxg
CVE: CVE-2026-54179
CWE: CWE-434, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-8hw4-7qjr-3wxg
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=6.0.0 <6.8.14
- Packagist: `backpack/crud` — affected >=7.0.0 <7.0.38

## Details
### Summary

`SingleBase64Image::uploadFiles` — the uploader bound to `image`-typed fields via `withFiles()` — only verifies that the submitted value starts with the string `data:image`. The MIME subtype and the base64-decoded bytes are never inspected or validated. A related bug in `FileNameGenerator` causes the stored file to receive an extensionless filename, because `mime_content_type()` returns `false` when given a data URI instead of a filesystem path.

The combination allows an authenticated admin to store a file of arbitrary type on the configured disk under a name without a recognizable extension.

### Details

```php
// src/app/Library/Uploaders/SingleBase64Image.php
if (Str::startsWith($value, 'data:image')) {
    // MIME subtype and decoded bytes are not validated
    $base64Image = Str::after($value, ';base64,');
    $finalPath   = $this->getPath() . $this->getFileName($value);
    Storage::disk($this->getDisk())->put($finalPath, base64_decode($base64Image));
    return $finalPath;
}

// src/app/Library/Uploaders/Support/FileNameGenerator.php
private function getExtensionFromFile(string|UploadedFile $file): string
{
    return is_a($file, UploadedFile::class, true)
        ? $file->extension()
        : Str::after(mime_content_type($file), '/'); // returns false on data URIs → empty string
}
```

The stored filename ends with a trailing dot and no extension.

### Impact

An authenticated admin submitting a malicious payload to a Backpack `image` field stored with `withFiles()` can write arbitrary file content to the configured storage disk. Depending on server configuration and how stored files are served, this may lead to stored XSS or other unintended behavior when the file is later accessed.

### Fix

The fix validates the declared MIME subtype against an allowlist, decodes the base64 payload, and verifies the actual file bytes with `finfo` before storing. The extension is derived from the detected MIME type rather than the data URI string. Applied in `SingleBase64Image::uploadFiles` and `uploadRepeatableFiles`; `FileNameGenerator::getExtensionFromFile` now rejects inputs that produce an empty extension.

Setting `X-Content-Type-Options: nosniff` on admin responses is a useful defense-in-depth complement.

### Affected versions

- `>= 6.0.0, < 6.8.14`
- `>= 7.0.0, < 7.0.38`

### Patched versions

- `6.8.14`
- `7.0.38`

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-8hw4-7qjr-3wxg
- https://github.com/Laravel-Backpack/CRUD
- https://github.com/Laravel-Backpack/CRUD/releases/tag/6.8.14
- https://github.com/Laravel-Backpack/CRUD/releases/tag/7.0.38
