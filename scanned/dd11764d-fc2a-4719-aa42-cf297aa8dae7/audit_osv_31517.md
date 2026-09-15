# [H] CVE-2025-13654

## Summary
Severity: High
Advisory: CVE-2025-13654
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-13654
Type: osv

## Details
A stack buffer overflow vulnerability exists in the buffer_get function of duc, a disk management tool, where a condition can evaluate to true due to underflow, allowing an out-of-bounds read.

## References
- https://github.com/zevv/duc/releases/tag/1.4.6
- https://hackingbydoing.wixsite.com/hackingbydoing/post/stack-buffer-overflow-in-duc
- https://kb.cert.org/vuls/id/441887
- https://www.kb.cert.org/vuls/id/441887
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13654.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-13654
- https://github.com/zevv/duc/commit/8638c4365ffd9e1966bdef8af6339dbee8c17e66
