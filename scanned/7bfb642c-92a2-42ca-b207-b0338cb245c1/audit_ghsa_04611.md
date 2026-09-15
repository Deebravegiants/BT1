# [C] CodeIgniter4 has a validation bypass when uploading file extensions via `ext_in` rule

## Summary
Severity: Critical
Advisory: GHSA-2gr4-ppc7-7mhx
CVE: CVE-2026-48062
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-2gr4-ppc7-7mhx
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.7.3

## Details
### Impact
The `ext_in` upload validation rule checked the MIME-derived guessed extension instead of the client-provided filename extension. As a result, an uploaded file named `shell.php` containing GIF-like content could pass validation such as:
```
uploaded[avatar]|is_image[avatar]|mime_in[avatar,image/gif]|ext_in[avatar,gif]
```
because the detected MIME type maps to `gif`, even though the uploaded filename extension is `php`.

Applications are impacted if they:
- accept user-controlled uploads,
- rely on `ext_in` to validate the uploaded filename extension,
- save uploaded files using the original client filename: `$file->move($path)`,
- store uploads in a web-accessible directory,
- and allow PHP or other executable files to run from that directory.

In those conditions, this may lead to arbitrary code execution. The default application does not expose such an upload endpoint.

### Patches
Upgrade to v4.7.3 or later.

### Workarounds
- Save uploads outside the public web root, preferably under `writable/uploads`
- Use `$file->store()` or `$file->move($path, $file->getRandomName())` instead of preserving the original filename
- Disable script execution in any public upload directory
- Manually verify the client filename extension before moving the file
- Reject files when `$file->getClientExtension()` is not in the allowed list or does not match `$file->guessExtension()`

### Resources
- [CodeIgniter4 uploaded files documentation](https://codeigniter.com/user_guide/libraries/uploaded_files.html#moving-files)
- [CodeIgniter4 file upload validation documentation](https://codeigniter.com/user_guide/libraries/validation.html#rules-for-file-uploads)
- [CWE-434: Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-2gr4-ppc7-7mhx
- https://github.com/codeigniter4/CodeIgniter4/commit/29299349e7d232e9532767c7cefaed30957309be
- https://codeigniter.com/user_guide/libraries/uploaded_files.html#moving-files
- https://codeigniter.com/user_guide/libraries/validation.html#rules-for-file-uploads
- https://github.com/codeigniter4/CodeIgniter4
- https://github.com/codeigniter4/CodeIgniter4/blob/develop/CHANGELOG.md
