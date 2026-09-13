# [H] CVE-2026-51583

## Summary
Severity: High
Advisory: CVE-2026-51583
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-51583
Type: osv

## Details
An issue in usememos through v0.30.0 allows a remote authenticated attacker to perform Server-Side Request Forgery (SSRF) via the Webhook validation mechanism in internal/webhook/validate.go, by setting a webhook target to an internal address.

## References
- https://gist.github.com/seiyaibuki0523/d8af15eb555808319a2633269a9ebb80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/51xxx/CVE-2026-51583.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-51583
- https://github.com/usememos/memos
