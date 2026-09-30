# [M] GNU Wget 1.25.0 Heap Buffer Overflow via convert_fname() in url.c

## Summary
Severity: Medium
Advisory: CVE-2026-58471
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-58471
Type: osv

## Details
GNU Wget through 1.25.0, fixed in commit c2640fe, contains a heap buffer overflow vulnerability in the convert_fname() function within src/url.c that allows remote attackers to trigger memory corruption through a server-supplied filename requiring character set conversion. When the output buffer is too small during iconv E2BIG reallocation, the reallocation logic miscalculates the remaining space, leading to a heap buffer overflow that can be exploited via a maliciously crafted server response.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58471.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58471
- https://www.vulncheck.com/advisories/gnu-wget-heap-buffer-overflow-via-convert-fname-in-url-c
- https://gitlab.com/gnuwget/wget/-/commit/c2640fe5171c59f87c58dc9fcb195b2d18b010ee
- https://gitlab.com/gnuwget/wget
