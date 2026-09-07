# [H]  cowlib cow_http_te module: Uncontrolled Resource Consumption vulnerability allows Excessive Allocation

## Summary
Severity: High
Advisory: GHSA-32p9-57cr-4x65
CVE: CVE-2026-7790
CWE: CWE-400
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-32p9-57cr-4x65
Type: github-advisory

## Affected
- Hex: `cowlib` — affected >=0.6.0 <2.16.1

## Details
Uncontrolled Resource Consumption vulnerability in ninenines cowlib (cow_http_te module) allows Excessive Allocation.

The chunked transfer-encoding parser in cow_http_te accepts an unbounded number of hex digits in the chunk-size field. Each digit causes a bignum multiplication (Len * 16 + digit), so parsing N hex digits requires O(N²) CPU work and O(N) memory. Additionally, when input is drip-fed, the parser discards the accumulated length on each partial read and restarts from zero on resumption, raising the cost to O(N³). An unauthenticated remote attacker can exploit this by sending an HTTP/1.1 request with Transfer-Encoding: chunked and a very long chunk-size hex string to cause denial of service through CPU exhaustion and memory amplification.

This vulnerability is associated with program file src/cow_http_te.erl and program routines cow_http_te:stream_chunked/2, cow_http_te:chunked_len/4.

This issue affects cowlib: from 0.6.0 before 2.16.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7790
- https://github.com/ninenines/cowlib/commit/a4b8039ce8c93ab00867ef6b7e888822c09f4369
- https://cna.erlef.org/cves/CVE-2026-7790.html
- https://github.com/ninenines/cowlib
- https://github.com/ninenines/cowlib/releases/tag/2.16.1
- https://osv.dev/vulnerability/EEF-CVE-2026-7790
