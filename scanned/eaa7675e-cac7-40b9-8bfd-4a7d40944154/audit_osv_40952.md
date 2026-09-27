# [M] Cap-go - Privilege Inversion in Build Log Stream via SSE Disconnect

## Summary
Severity: Medium
Advisory: CVE-2026-56280
Aliases: GHSA-95g7-xwwx-j737
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56280
Type: osv

## Details
Cap-go before 12.128.2 contains a privilege inversion vulnerability in GET /build/logs/:jobId that allows read-only API key holders to cancel running native builds. The endpoint registers an abort listener on the SSE stream that unconditionally invokes cancelBuildOnDisconnect() using the privileged server-side BUILDER_API_KEY when clients disconnect, bypassing the app.build_native permission check required by the explicit POST /build/cancel/:jobId endpoint. Attackers with read-only API keys can repeatedly disrupt native build operations and CI/CD workflows by opening the log stream and dropping the connection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56280.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-95g7-xwwx-j737
- https://nvd.nist.gov/vuln/detail/CVE-2026-56280
- https://www.vulncheck.com/advisories/cap-go-privilege-inversion-in-build-log-stream-via-sse-disconnect
