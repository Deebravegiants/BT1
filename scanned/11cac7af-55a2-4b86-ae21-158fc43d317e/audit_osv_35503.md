# [H] OOBR and OOBW in libpcap before 1.10.7

## Summary
Severity: High
Advisory: CVE-2026-0799
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-0799
Type: osv

## Details
In BPF instructions that load/store a value from/to a scratch memory register the register index is an unsigned 32-bit integer and must not exceed 15, but libpcap BPF interpreter does not validate the value.  In particular uncommon use cases a crafted filter program can cause the interpreter to try reading and writing the OS process memory in the 16GiB starting at the current stack frame on 64-bit architectures and in the entire address space on 32-bit architectures.

## References
- https://github.com/the-tcpdump-group/libpcap/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0799.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0799
- https://github.com/the-tcpdump-group/libpcap/commit/48e8960a7108e9e828f9d7bdc7e97bdab841aec7
