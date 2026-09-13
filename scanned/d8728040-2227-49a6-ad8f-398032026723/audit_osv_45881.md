# [M] curl would wrongly reuse an existing HTTP proxy connection doing CONNECT to a server, even if the...

## Summary
Severity: Medium
Advisory: JLSEC-2026-438
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-438
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.18.0+0

## Details
curl would wrongly reuse an existing HTTP proxy connection doing CONNECT to a
server, even if the new request uses different credentials for the HTTP proxy.
The proper behavior is to create or use a separate connection.

## References
- http://www.openwall.com/lists/oss-security/2026/03/11/3
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://curl.se/docs/CVE-2026-3784.html
- https://curl.se/docs/CVE-2026-3784.json
- https://github.com/advisories/GHSA-5q3w-6p3j-mw6p
- https://hackerone.com/reports/3584903
- https://nvd.nist.gov/vuln/detail/CVE-2026-3784
