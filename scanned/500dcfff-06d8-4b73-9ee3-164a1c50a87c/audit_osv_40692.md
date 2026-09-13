# [H] Tinyproxy - HTTP Request Smuggling via CL/TE Desynchronization

## Summary
Severity: High
Advisory: CVE-2026-54387
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-54387
Type: osv

## Details
Tinyproxy through 1.11.3, fixed in commit ff45d3b, fails to reconcile conflicting Content-Length and Transfer-Encoding: chunked headers, forwarding both verbatim to the backend while using Content-Length to determine how many request body bytes to consume. Remote attackers can desynchronize the proxy and backend parser state, allowing injection of arbitrary HTTP requests to the backend to enable cache poisoning, access control bypass, and request hijacking.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54387.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54387
- https://www.vulncheck.com/advisories/tinyproxy-http-request-smuggling-via-cl-te-desynchronization
- https://github.com/tinyproxy/tinyproxy/issues/609
- https://github.com/tinyproxy/tinyproxy/pull/610
- https://github.com/tinyproxy/tinyproxy/commit/ff45d3bf0e61d0f8ed97ab379d3047f04eb67521
- https://github.com/tinyproxy/tinyproxy
