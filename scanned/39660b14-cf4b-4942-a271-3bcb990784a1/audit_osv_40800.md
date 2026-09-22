# [M] Snipe-IT: Improper Authorization in File Deletion (IDOR)

## Summary
Severity: Medium
Advisory: CVE-2026-55519
Aliases: GHSA-x667-r589-43m7
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-55519
Type: osv

## Details
Snipe-IT is an IT asset/license management system. Prior to 8.4.1, an authenticated user with generic asset edit permission can delete files attached to assets outside the user's ownership or company assignment. The destroy() methods in app/Http/Controllers/Api/UploadedFilesController.php and app/Http/Controllers/UploadedFilesController.php authorize update against the object class instead of the resolved object instance, creating an insecure direct object reference. This issue is fixed in version 8.4.1.

## References
- https://github.com/grokability/snipe-it/releases/tag/v8.4.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55519.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-x667-r589-43m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-55519
- https://github.com/grokability/snipe-it/commit/8bc7d50e35d93eee5a0d48b4923e497937cf93fd
