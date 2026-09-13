# [M] GNU Wget through 1.25.0, fixed in commit c2640fe, contains a heap buffer overflow vulnerability...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1160
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1160
Type: osv

## Affected
- Julia: `wget_jll` — affected unspecified

## Details
GNU Wget through 1.25.0, fixed in commit c2640fe, contains a heap buffer overflow vulnerability in the `convert_fname()` function within `src/url.c` that allows remote attackers to trigger memory corruption through a server-supplied filename requiring character set conversion. When the output buffer is too small during iconv E2BIG reallocation, the reallocation logic miscalculates the remaining space, leading to a heap buffer overflow that can be exploited via a maliciously crafted server response.

## References
- https://github.com/advisories/GHSA-vv88-699v-w5rh
- https://gitlab.com/gnuwget/wget/-/commit/c2640fe5171c59f87c58dc9fcb195b2d18b010ee
- https://nvd.nist.gov/vuln/detail/CVE-2026-58471
- https://www.vulncheck.com/advisories/gnu-wget-heap-buffer-overflow-via-convert-fname-in-url-c
