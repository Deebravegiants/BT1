# [M] Nightingale 9.1.1 SSRF Guard Bypass via IPv6 Encoding

## Summary
Severity: Medium
Advisory: CVE-2026-85692
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85692
Type: osv

## Details
Nightingale (n9e), as of commit 8362cbe (main branch, confirmed 2026-08-27), contains a server-side request forgery vulnerability in the isPublicIP function in aiagent/tools/http.go, the SSRF guard for the http_fetch AI-agent tool. The function only unwraps standard IPv4-mapped (::ffff:a.b.c.d) IPv6 addresses before checking them against the forbidden-range list, and does not classify 6to4 (2002::/16), NAT64 (64:ff9b::/96, 64:ff9b:1::/48), or deprecated site-local (fec0::/10) addresses. On a dual-stack or NAT64-enabled host, an attacker able to supply a URL to the http_fetch tool can bypass the guard by encoding a forbidden IPv4 address (such as the cloud instance-metadata endpoint 169.254.169.254) in one of these IPv6 forms to reach internal or metadata services.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85692.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85692
- https://www.vulncheck.com/advisories/nightingale-9.1.1-ssrf-guard-bypass-via-ipv6-encoding
- https://github.com/ccfos/nightingale/issues/3363
- https://github.com/ccfos/nightingale
- https://github.com/ccfos/nightingale/blob/v9.1.1/aiagent/tools/http.go
