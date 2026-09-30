# [C] FreeRDP before 3.29.0 HTTP Proxy Request Injection via Redirection

## Summary
Severity: Critical
Advisory: CVE-2026-67289
Aliases: GHSA-mwwh-mhp9-q7vm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67289
Type: osv

## Details
FreeRDP before 3.29.0 (affected versions <= 3.28.0) does not validate CRLF and control characters in the server-controlled RDP redirection TargetNetAddress field. This value is copied into the client's ServerHostname and, when the client connects through an HTTP proxy, is written directly into the proxy CONNECT request line and Host header by http_proxy_connect() without filtering. A malicious or compromised RDP server can send a crafted redirection PDU containing embedded control characters to inject arbitrary headers/requests into the HTTP proxy CONNECT request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67289.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-mwwh-mhp9-q7vm
- https://nvd.nist.gov/vuln/detail/CVE-2026-67289
- https://www.vulncheck.com/advisories/freerdp-before-http-proxy-request-injection-via-redirection
- https://github.com/FreeRDP/FreeRDP/commit/f3b4347105114fe7453828736bea069999af319f
