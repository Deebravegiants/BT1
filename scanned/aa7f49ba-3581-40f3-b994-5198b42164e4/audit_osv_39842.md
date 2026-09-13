# [H] Unbounded recursion over attacker-controlled PDF outline tree in Spring AI PDF Document Reader

## Summary
Severity: High
Advisory: CVE-2026-47851
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47851
Type: osv

## Details
Analyzing a PDF with a deeply nested or cyclic table of contents can cause a StackOverflowError in the ingestion thread.
Spring AI 2.0.0
Spring AI 1.1.0 - 1.1.8
Spring AI 1.0.0 - 1.0.9

## References
- https://spring.io/security/cve-2026-47851
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47851.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47851
