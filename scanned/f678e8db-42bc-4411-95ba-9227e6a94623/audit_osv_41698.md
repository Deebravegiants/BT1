# [M] stoatchat before 0.13.5 Unauthenticated SSRF via proxy and embed endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-63306
Aliases: GHSA-xhww-5g9p-vvq5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-63306
Type: osv

## Details
stoatchat before 0.13.5 contains an unauthenticated server-side request forgery vulnerability in the /proxy and /embed endpoints that accept arbitrary URLs without DNS resolution filtering or private IP range validation. Attackers can enumerate internal services, fingerprint applications, and reach instance metadata endpoints by supplying malicious URLs or leveraging redirect chains to access internal infrastructure.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63306.json
- https://github.com/stoatchat/stoatchat/security/advisories/GHSA-xhww-5g9p-vvq5
- https://nvd.nist.gov/vuln/detail/CVE-2026-63306
- https://www.vulncheck.com/advisories/stoatchat-before-unauthenticated-ssrf-via-proxy-and-embed-endpoints
