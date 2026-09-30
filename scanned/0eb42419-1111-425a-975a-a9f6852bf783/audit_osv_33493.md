# [M] CVE-2025-43903

## Summary
Severity: Medium
Advisory: CVE-2025-43903
CVSS: 4.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-43903
Type: osv

## Details
NSSCryptoSignBackend.cc in Poppler before 25.04.0 does not verify the adbe.pkcs7.sha1 signatures on documents, resulting in potential signature forgeries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/43xxx/CVE-2025-43903.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-43903
- https://gitlab.freedesktop.org/poppler/poppler/-/commit/f1b9c830f145a0042e853d6462b2f9ca4016c669
