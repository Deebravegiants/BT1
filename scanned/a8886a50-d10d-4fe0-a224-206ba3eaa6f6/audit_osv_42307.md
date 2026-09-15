# [M] facil.io 0.6.0 - 0.7.6 Infinite Loop DoS via Multipart MIME Body Parser

## Summary
Severity: Medium
Advisory: CVE-2026-66730
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66730
Type: osv

## Details
facil.io 0.6.0 through 0.7.6 contains a denial-of-service vulnerability in the multipart body parser that allows an unauthenticated remote attacker to permanently freeze worker processes at 100% CPU by sending a multipart/form-data request with a partial closing boundary. The missing progress guard in the parser loop causes http_mime_parse to return 0 bytes consumed without setting done or error flags, causing the calling loop to re-invoke the parser on the same buffer indefinitely, exhausting all workers and permanently disabling the server until manually restarted.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66730.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66730
- https://www.vulncheck.com/advisories/facil-io-infinite-loop-dos-via-multipart-mime-body-parser
- https://github.com/boazsegev/facil.io
- https://github.com/theopaid/Infinite-Loop-DoS-in-facil.io-MIME-Parser
- https://tpaidakis.com/writeups/facilio-parser-dos/
