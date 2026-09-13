# [M] Intelliants Subrion CMS - Path Traversal

## Summary
Severity: Medium
Advisory: CVE-2026-72604
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72604
Type: osv

## Details
A path traversal vulnerability in Intelliants Subrion CMS through 4.2.1 allows authenticated administrators to delete arbitrary files on the server via the admin panel file deletion endpoint. The endpoint passes a user-supplied file path directly to unlink() without sanitization or path canonicalization. An authenticated administrator can delete sensitive system files outside the web root, potentially causing server instability or facilitating further attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72604.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72604
- https://github.com/intelliants/subrion
