# [M] facil.io 0.6.0 - 0.7.6 Integer Underflow DoS via Multipart MIME Body Parser

## Summary
Severity: Medium
Advisory: CVE-2026-66729
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66729
Type: osv

## Details
facil.io 0.6.0 through 0.7.6 contains an integer underflow vulnerability in the multipart MIME body parser that allows unauthenticated remote attackers to crash the server process by sending a crafted Content-Disposition header with an empty field name. Attackers can trigger a uint32_t wraparound in http_mime_parser.h causing an out-of-bounds memory read past the name pointer, resulting in a bus fault that crashes the handling worker with a single POST request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66729.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66729
- https://www.vulncheck.com/advisories/facil-io-integer-underflow-dos-via-multipart-mime-body-parser
- https://github.com/boazsegev/facil.io
- https://github.com/theopaid/Out-of-Bounds-Read-in-facil.io-MIME-Parser-leads-to-Server-Crash
- https://tpaidakis.com/writeups/facilio-parser-dos/
