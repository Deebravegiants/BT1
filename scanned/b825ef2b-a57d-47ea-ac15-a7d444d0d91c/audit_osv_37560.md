# [M] OOBR in libpcap before 1.10.7

## Summary
Severity: Medium
Advisory: CVE-2026-31912
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-31912
Type: osv

## Details
libpcap BPF interpreter detects neither reaching the end of the filter program buffer due to lack of a return instruction nor executing a jump instruction with an offset that translates to a pointer outside of the buffer.  In particular uncommon use cases a crafted filter program can cause the interpreter to try reading the OS process memory in the 32GiB around the buffer on 64-bit architectures and in the entire address space on 32-bit architectures.

## References
- https://github.com/the-tcpdump-group/libpcap/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31912.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31912
- https://github.com/the-tcpdump-group/libpcap/commit/d3f358d3cffbe1ecb94d5284b3e81f052a0adcb9
