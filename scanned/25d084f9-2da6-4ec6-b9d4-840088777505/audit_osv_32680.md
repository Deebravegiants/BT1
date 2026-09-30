# [M] wb2osz/direwolf <= 1.8.1 Stack-based Buffer Overflow DoS

## Summary
Severity: Medium
Advisory: CVE-2025-34457
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2025-34457
Type: osv

## Details
wb2osz/direwolf (Dire Wolf) versions up to and including 1.8, prior to commit 694c954, contain a stack-based buffer overflow vulnerability in the function kiss_rec_byte() located in src/kiss_frame.c. When processing crafted KISS frames that reach the maximum allowed frame length (MAX_KISS_LEN), the function appends a terminating FEND byte without reserving sufficient space in the stack buffer. This results in an out-of-bounds write followed by an out-of-bounds read during the subsequent call to kiss_unwrap(), leading to stack memory corruption or application crashes. This vulnerability may allow remote unauthenticated attackers to trigger a denial-of-service condition.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34457.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34457
- https://www.vulncheck.com/advisories/wb2osz-direwolf-stack-based-buffer-overflow-dos
- https://github.com/wb2osz/direwolf/issues/617
- https://github.com/wb2osz/direwolf/commit/694c954
- https://github.com/wb2osz/direwolf
- https://github.com/marlinkcyber/advisories/blob/main/advisories/MCSAID-2025-010-direwolf-stack-buffer-overflow-kiss-frame.md
