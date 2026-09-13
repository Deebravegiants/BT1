# [C] CodeIgniter: Uploaded file extension validation bypass in `is_image` and `mime_in` rules

## Summary
Severity: Critical
Advisory: GHSA-mmj4-63m4-r6h5
CVE: CVE-2026-63223
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-mmj4-63m4-r6h5
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.7.4

## Details
### Impact
This is an unsafe file upload validation vulnerability that can lead to remote code execution in vulnerable application configurations.

Applications are impacted when they:
- validate uploads using `is_image` or `mime_in` without an independent safe extension check, such as `ext_in` on patched versions
- save uploaded files using the client-supplied filename
- place uploads in a web-accessible directory where PHP files can execute

### Patches
Upgrade to v4.7.4 or later.

### Workarounds
- Save uploads outside the public web root, preferably under `writable/uploads`.
- Use `$file->store()` or `$file->move($path, $file->getRandomName())` instead of preserving the original client filename.
- Disable script execution in any public upload directory.
- Manually verify the client filename extension before moving the file.
- For image uploads, reject files when `$file->getClientExtension()` is not an allowed image extension.
- For exact MIME-type validation, reject files when `$file->getClientExtension()` does not match `$file->guessExtension()`.

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-mmj4-63m4-r6h5
- https://nvd.nist.gov/vuln/detail/CVE-2026-63223
- https://github.com/codeigniter4/CodeIgniter4/commit/b6e9a4fa1dca2df3d3f261bdf61532df8c6420aa
- https://github.com/codeigniter4/CodeIgniter4
- https://github.com/codeigniter4/CodeIgniter4/releases/tag/v4.7.4
