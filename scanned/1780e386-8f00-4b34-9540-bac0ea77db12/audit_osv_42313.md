# [M] Rouille 0.1.6 - 3.6.2 Reachable Assertion DoS via remove_prefix percent-encoding

## Summary
Severity: Medium
Advisory: CVE-2026-66754
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-66754
Type: osv

## Details
Rouille 0.1.6 through 3.6.2 contains a reachable assertion vulnerability in the Request::remove_prefix function that allows remote unauthenticated attackers to crash the server by sending a crafted percent-encoded URL. Attackers can send a request whose decoded path matches a configured prefix while the raw percent-encoded path does not, causing the assert! to fail and triggering either a 500 error or full process termination depending on the panic configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66754.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66754
- https://www.vulncheck.com/advisories/rouille-reachable-assertion-dos-via-remove-prefix-percent-encoding
- https://github.com/tomaka/rouille
- https://github.com/theopaid/Remote-Denial-of-Service-via-Reachable-Assertion-in-URL-Prefix-Handling-rouille-
