# [M] CVE-2025-60319

## Summary
Severity: Medium
Advisory: CVE-2025-60319
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-60319
Type: osv

## Details
PerfreeBlog v4.0.11 is vulnerable to Server-Side Request Forgery due to a missing authorization check in the uploadAttachByUrl API endpoint (AttachController.java).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60319.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60319
- https://github.com/PerfreeBlog/PerfreeBlog/issues/20
- https://github.com/PerfreeBlog/PerfreeBlog/commit/103c79165e3a41a1729188fdc8a1e90c97c0a06d
