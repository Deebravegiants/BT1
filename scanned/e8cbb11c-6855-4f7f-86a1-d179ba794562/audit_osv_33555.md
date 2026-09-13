# [H] CVE-2025-46205

## Summary
Severity: High
Advisory: CVE-2025-46205
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-46205
Type: osv

## Details
A heap-use-after free in the PdfTokenizer::ReadDictionary function of podofo v0.10.0 to v0.10.5 allows attackers to cause a Denial of Service (DoS) by supplying a crafted PDF file. NOTE: this is disputed by the Supplier because there is no available file to reproduce the issue.

## References
- https://github.com/ShadowByte1/CVE-Reports/blob/main/CVE-2025-46205.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46205.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46205
- https://github.com/ShadowByte1/CVE-Reports/issues/1
- https://github.com/podofo/podofo
