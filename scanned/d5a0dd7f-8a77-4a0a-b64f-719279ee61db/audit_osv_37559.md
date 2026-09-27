# [M] abort() in libpcap before 1.10.7 on an invalid BPF opcode

## Summary
Severity: Medium
Advisory: CVE-2026-31911
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-31911
Type: osv

## Details
libpcap BPF interpreter calls abort() if it encounters a BPF instruction that has an invalid opcode.  In particular uncommon use cases a crafted filter program can terminate the OS process.

## References
- https://github.com/the-tcpdump-group/libpcap/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31911.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31911
- https://github.com/the-tcpdump-group/libpcap/commit/a715bcdde830299cba4171514385cb17ec19b6e9
