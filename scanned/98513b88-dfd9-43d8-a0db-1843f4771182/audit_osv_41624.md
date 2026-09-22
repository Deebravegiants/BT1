# [M] division by zero in libpcap before 1.10.7

## Summary
Severity: Medium
Advisory: CVE-2026-6244
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-6244
Type: osv

## Details
libpcap BPF interpreter for the 'div #k' and 'mod #k' ALU instructions does not check whether the immediate value is zero.  In particular uncommon use cases a crafted filter program can cause a division by zero.

## References
- https://github.com/the-tcpdump-group/libpcap/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6244.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6244
- https://github.com/the-tcpdump-group/libpcap/commit/98bb921b141aa642faedbf2ac510541c76499a19
