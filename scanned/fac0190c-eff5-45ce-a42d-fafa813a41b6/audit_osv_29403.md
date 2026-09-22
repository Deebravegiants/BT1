# [C] tipc: Return non-zero value from tipc_udp_addr2str() on error

## Summary
Severity: Critical
Advisory: CVE-2024-42284
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42284
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: Return non-zero value from tipc_udp_addr2str() on error

tipc_udp_addr2str() should return non-zero value if the UDP media
address is invalid. Otherwise, a buffer overflow access can occur in
tipc_media_addr_printf(). Fix this by returning 1 on an invalid UDP
media address.

## References
- https://git.kernel.org/stable/c/253405541be2f15ffebdeac2f4cf4b7e9144d12f
- https://git.kernel.org/stable/c/2abe350db1aa599eeebc6892237d0bce0f1de62a
- https://git.kernel.org/stable/c/5eea127675450583680c8170358bcba43227bd69
- https://git.kernel.org/stable/c/728734352743a78b4c5a7285b282127696a4a813
- https://git.kernel.org/stable/c/76ddf84a52f0d8ec3f5db6ccce08faf202a17d28
- https://git.kernel.org/stable/c/7ec3335dd89c8d169e9650e4bac64fde71fdf15b
- https://git.kernel.org/stable/c/aa38bf74899de07cf70b50cd17f8ad45fb6654c8
- https://git.kernel.org/stable/c/fa96c6baef1b5385e2f0c0677b32b3839e716076
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42284.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
