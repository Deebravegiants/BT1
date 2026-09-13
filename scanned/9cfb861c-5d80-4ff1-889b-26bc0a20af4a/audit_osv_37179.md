# [M] Integer Underflow in Lexbor ISO‑2022‑JP Encoder

## Summary
Severity: Medium
Advisory: CVE-2026-29078
Aliases: GHSA-mrwr-xh7f-96v3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-29078
Type: osv

## Details
Lexbor is a web browser engine library. Prior to 2.7.0, the ISO‑2022‑JP encoder in Lexbor fails to reset the temporary size variable between iterations. The statement ctx->buffer_used -= size with a stale size = 3 causes an integer underflow that wraps to SIZE_MAX. Afterwards, memcpy is called with a negative length, leading to an out‑of‑bounds read from the stack and an out‑of‑bounds write to the heap. The source data is partially controllable via the contents of the DOM tree. This vulnerability is fixed in 2.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29078.json
- https://github.com/lexbor/lexbor/security/advisories/GHSA-mrwr-xh7f-96v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-29078
