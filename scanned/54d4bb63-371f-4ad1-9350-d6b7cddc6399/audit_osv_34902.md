# [M] CVE-2025-66370

## Summary
Severity: Medium
Advisory: CVE-2025-66370
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2025-11-28
Source: https://osv.dev/vulnerability/CVE-2025-66370
Type: osv

## Details
Kivitendo before 3.9.2 allows XXE injection. By uploading an electronic invoice in the ZUGFeRD format, it is possible to read and exfiltrate files from the server's filesystem.

## References
- https://github.com/kivitendo/kivitendo-erp/blob/fd3f993fc731cbcaa5eb87d55df7c82df4df9c09/doc/changelog
- https://invoice.secvuln.info
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66370.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66370
- https://github.com/kivitendo/kivitendo-erp/commit/1286dee72f9919166178d0cdb5f52f13b0f7d4de
- https://github.com/kivitendo/kivitendo-erp/commit/f6ba56bd8d22a428534057589baace6b7bfdf2e9
- https://blog.kivitendo.de/?p=1415
