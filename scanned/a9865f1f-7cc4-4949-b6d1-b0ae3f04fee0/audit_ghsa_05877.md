# [H] CodeIgniter: Path traversal in UploadedFile::move() when using client-provided filenames

## Summary
Severity: High
Advisory: GHSA-hhmc-q9hp-r662
CVE: CVE-2026-63222
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-hhmc-q9hp-r662
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.7.4

## Details
### Impact
In affected versions, calling `UploadedFile::move()` **without a second argument** uses the client-provided filename without sanitization. Depending on the destination path and server configuration, an attacker can supply a filename containing path traversal sequences (e.g. `../../public/shell.php`) to write uploaded content outside the intended upload directory.

The patch sanitizes this default (no-argument) path.

**Note:** The patch only sanitizes the filename when no second argument is passed. If your application **explicitly** passes a client-provided name as the second argument, you remain responsible for sanitizing it - the patch does not (and cannot) sanitize a caller-supplied filename:
```php
// Unsafe - even after upgrading:
$file->move(WRITEPATH . 'uploads', $file->getName());
$file->move(WRITEPATH . 'uploads', $file->getClientName());
```

### Patches
Upgrade to v4.7.4 or later.

### Workarounds
If you cannot upgrade immediately, use a generated filename or sanitize the client filename before passing it to `move()`.

Use a generated filename:
```php
$file->move(WRITEPATH . 'uploads', $file->getRandomName());
```
Or sanitize the client filename before passing it to `move()`:
```php
helper('security');

$name = sanitize_filename($file->getClientName());
$file->move(WRITEPATH . 'uploads', $name);
```

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-hhmc-q9hp-r662
- https://nvd.nist.gov/vuln/detail/CVE-2026-63222
- https://github.com/codeigniter4/CodeIgniter4/commit/20ebcf4694d96d3c97fbc3938e360730e4f54618
- https://github.com/codeigniter4/CodeIgniter4
- https://github.com/codeigniter4/CodeIgniter4/releases/tag/v4.7.4
