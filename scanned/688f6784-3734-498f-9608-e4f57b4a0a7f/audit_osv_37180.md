# [M] Type Confusion in Lexbor Fragment Parser

## Summary
Severity: Medium
Advisory: CVE-2026-29079
Aliases: GHSA-mrpr-v36q-2vp8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-29079
Type: osv

## Details
Lexbor is a web browser engine library. Prior to 2.7.0, a type‑confusion vulnerability exists in Lexbor’s HTML fragment parser. When ns = UNDEF, a comment is created using the “unknown element” constructor. The comment’s data are written into the element’s fields via an unsafe cast, corrupting the qualified_name field. That corrupted value is later used as a pointer and dereferenced near the zero page. This vulnerability is fixed in 2.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29079.json
- https://github.com/lexbor/lexbor/security/advisories/GHSA-mrpr-v36q-2vp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-29079
