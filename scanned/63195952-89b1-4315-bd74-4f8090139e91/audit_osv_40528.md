# [M] Integer Overflow in fzf

## Summary
Severity: Medium
Advisory: CVE-2026-53432
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-53432
Type: osv

## Details
fzf is vulnerable to Integer Overflow leading to crash in FuzzyMatchV2 function. When input line length is approximately 2,200,000 bytes and pattern length is 999 bytes, the product overflows. The Go runtime detects the invalid slice bounds and terminates the process immediately with a non-recoverable panic.

This issue was fixed in version 0.73.1.

## References
- https://cert.pl/en/posts/2026/06/CVE-2026-53432
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53432.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53432
- https://github.com/junegunn/fzf/commit/ccedd064ca56921a4235219516b3d834f60e7b91
- https://github.com/junegunn/fzf
