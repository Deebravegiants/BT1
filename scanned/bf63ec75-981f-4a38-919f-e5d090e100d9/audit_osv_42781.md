# [H] Memos Webhook DNS Rebinding TOCTOU SSRF in safeDialContext()

## Summary
Severity: High
Advisory: CVE-2026-71272
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71272
Type: osv

## Details
Memos' webhook dispatch function safeDialContext (internal/webhook/webhook.go) resolves the target hostname via net.DefaultResolver.LookupHost and validates the resulting IPs against reserved ranges, but then dials net.JoinHostPort(host, port) using the original hostname rather than the already-validated IP address.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71272.json
- https://github.com/usememos/memos
- https://github.com/usememos/memos/blob/main/internal/webhook/webhook.go
- https://nvd.nist.gov/vuln/detail/CVE-2026-71272
