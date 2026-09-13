# [M] SiYuan before v3.8.1 SSRF via DNS-Rebinding TOCTOU

## Summary
Severity: Medium
Advisory: CVE-2026-82234
Aliases: GHSA-x8gv-g2g3-65fj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82234
Type: osv

## Details
SiYuan versions before v3.8.1 contain a server-side request forgery vulnerability in the http_request and web_fetch agent tools that perform DNS resolution only at guard time without validating the connect-time resolution. Attackers can use DNS rebinding to answer the guard resolution with a public IP and the connect resolution with a private or metadata IP, bypassing the SSRF defense to access cloud instance metadata and internal services.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82234.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-x8gv-g2g3-65fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-82234
- https://www.vulncheck.com/advisories/siyuan-before-3.8.1-ssrf-via-dns-rebinding-toctou
