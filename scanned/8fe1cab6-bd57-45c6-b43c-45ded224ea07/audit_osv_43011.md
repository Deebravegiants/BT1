# [C] ipvs: ensure inner headers in ICMP errors are in headroom

## Summary
Severity: Critical
Advisory: CVE-2026-72319
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72319
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: ensure inner headers in ICMP errors are in headroom

Sashiko points out that after stripping the outer headers
with pskb_pull() we should ensure the inner IP headers
in ICMP errors from tunnels are present in the skb headroom
for functions like ipv4_update_pmtu(), icmp_send() and
IP_VS_DBG().

Also, add more checks for the length of the inner headers.

## References
- https://git.kernel.org/stable/c/19657b3a17b774ae4e2f2635b5ae8638c9344a40
- https://git.kernel.org/stable/c/3f7a535ff0fa627a0132803e4c2f903ceffcbc1c
- https://git.kernel.org/stable/c/8f48cfe657409fb5c7ba0521b14da6d47546d9cf
- https://git.kernel.org/stable/c/92185d6f7819bc558939ae83de7b1abe90e3b5c2
- https://git.kernel.org/stable/c/9bc9b95aee2b2e3f1301a16a67ee504960402875
- https://git.kernel.org/stable/c/a735f9964a3d9ed97daf9b08507f8b5bcafe6326
- https://git.kernel.org/stable/c/dac813101914c21219ac221a60a31a11bc90e7ec
- https://git.kernel.org/stable/c/dd22f74a09e25ca298ced0a3763ef353242cb78d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72319.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72319
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
