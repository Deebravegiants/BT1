# [H] net: dsa: mv88e6xxx: Fix out-of-bound access

## Summary
Severity: High
Advisory: CVE-2024-44988
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44988
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.323, >=4.20.0 <5.4.283, >=5.0.0 <5.10.225, >=5.5.0 <5.15.166, >=5.11.0 <6.1.107, >=5.16.0 <6.6.48, >=6.2.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: mv88e6xxx: Fix out-of-bound access

If an ATU violation was caused by a CPU Load operation, the SPID could
be larger than DSA_MAX_PORTS (the size of mv88e6xxx_chip.ports[] array).

## References
- https://git.kernel.org/stable/c/050e7274ab2150cd212b2372595720e7b83a15bd
- https://git.kernel.org/stable/c/18b2e833daf049223ab3c2efdf8cdee08854c484
- https://git.kernel.org/stable/c/4a88fca95c8df3746b71e31f44a02d35f06f9864
- https://git.kernel.org/stable/c/528876d867a23b5198022baf2e388052ca67c952
- https://git.kernel.org/stable/c/a10d0337115a6d223a1563d853d4455f05d0b2e3
- https://git.kernel.org/stable/c/d39f5be62f098fe367d672b4dd4bc4b2b80e08e7
- https://git.kernel.org/stable/c/f7d8c2fabd39250cf2333fbf8eef67e837f90a5d
- https://git.kernel.org/stable/c/f87ce03c652dba199aef15ac18ade3991db5477e
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44988.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
