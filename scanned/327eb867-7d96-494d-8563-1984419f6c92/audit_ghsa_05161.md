# [H] gun has an Uncontrolled Resource Consumption vulnerability

## Summary
Severity: High
Advisory: GHSA-r53j-fjj5-mv77
CVE: CVE-2026-43973
CWE: CWE-770
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-r53j-fjj5-mv77
Type: github-advisory

## Affected
- Hex: `gun` — affected >=1.0.0 <2.4.0

## Details
Uncontrolled Resource Consumption vulnerability in ninenines gun (gun_http module) allows a malicious server to exhaust client memory via unbounded HTTP/1.1 response buffering.

In gun_http:handle/5, three clauses accumulate incoming TCP data into the connection's buffer field using binary concatenation with no upper-bound check: the head clause appends data until the \r\n\r\n header terminator is found; the body_chunked clause appends data whenever cow_http_te:stream_chunked/2 returns a more result indicating an incomplete chunk boundary; and the body_trailer clause appends data until the trailing \r\n\r\n is found. In each case, when the expected terminator never arrives, the enlarged binary is stored back into state and the process waits for more data, with no configurable or hard-coded ceiling on buffer size.

A malicious or compromised server can exploit this by sending a partial response that never completes. For example, a response may begin with HTTP/1.1 200 OK\r\nX-Pad:  followed by an unbounded stream of arbitrary bytes, never sending the header terminator. The gun connection process will continuously append the incoming data to its buffer, causing unbounded heap growth. Because BEAM imposes no per-process heap limit by default, a single malicious connection can exhaust all available memory on the node, causing a node-wide out-of-memory crash.

This issue affects gun: from 1.0.0 before 2.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43973
- https://github.com/ninenines/gun/commit/f3e7e0568b3c4cf9fa4bea79d5116e67ce76ad25
- https://cna.erlef.org/cves/CVE-2026-43973.html
- https://github.com/ninenines/gun
- https://osv.dev/vulnerability/EEF-CVE-2026-43973
