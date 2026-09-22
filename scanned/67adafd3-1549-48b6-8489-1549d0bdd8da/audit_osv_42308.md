# [M] facil.io 0.7.5 - 0.7.6 HTTP/1.1 Chunked Transfer Encoding Parser Crash DoS

## Summary
Severity: Medium
Advisory: CVE-2026-66731
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66731
Type: osv

## Details
facil.io 0.7.5 through 0.7.6 contains a denial-of-service vulnerability in the HTTP/1.1 chunked transfer encoding parser that allows unauthenticated remote attackers to crash the server by sending a negative chunk size value. Attackers can send a single POST request with a Transfer-Encoding: chunked header containing a leading minus sign in the chunk size field, causing the parser in http1_parser.h to compute a large positive integer from the negated value, corrupting internal state and moving the read pointer into unmapped memory resulting in a fault.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66731.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66731
- https://www.vulncheck.com/advisories/facil-io-http-chunked-transfer-encoding-parser-crash-dos
- https://github.com/boazsegev/facil.io
- https://github.com/theopaid/Negative-Chunk-Size-Parsing-Causes-Memory-Corruption-in-facil.io-leading-to-Server-Crash
- https://tpaidakis.com/writeups/facilio-parser-dos/
