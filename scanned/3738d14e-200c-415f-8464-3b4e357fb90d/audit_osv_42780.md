# [H] Memos Webhook SSRF via 0.0.0.0 Reserved-IP Bypass

## Summary
Severity: High
Advisory: CVE-2026-71271
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71271
Type: osv

## Details
Memos' webhook URL validation, isReservedIP (internal/webhook/validate.go), checks a candidate IP against a reservedCIDRs list that omits 0.0.0.0/8 and never calls ip.IsUnspecified — unlike the correctly implemented sibling function isInternalIP in internal/httpgetter/html_meta.go, which does.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71271.json
- https://github.com/usememos/memos
- https://github.com/usememos/memos/blob/main/internal/webhook/validate.go
- https://nvd.nist.gov/vuln/detail/CVE-2026-71271
