# [M] GNU Wget 1.25.0 Heap Buffer Overflow via HTML Attribute Encoding

## Summary
Severity: Medium
Advisory: CVE-2026-58472
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-58472
Type: osv

## Details
GNU Wget through 1.25.0, fixed in commit dd692d9, contains a heap buffer overflow vulnerability in the html_quote_string() function in src/convert.c that allows a remote attacker to trigger memory corruption by supplying a crafted HTML attribute with a large number of characters requiring entity encoding. A server-supplied HTML attribute causes a signed integer counter to overflow during output size accumulation, resulting in an undersized heap allocation and subsequent heap buffer overflow during the copy phase.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58472.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58472
- https://www.vulncheck.com/advisories/gnu-wget-heap-buffer-overflow-via-html-attribute-encoding
- https://gitlab.com/gnuwget/wget/-/commit/dd692d9cea5335b181d877ae917fe6e75587a812
- https://gitlab.com/gnuwget/wget
