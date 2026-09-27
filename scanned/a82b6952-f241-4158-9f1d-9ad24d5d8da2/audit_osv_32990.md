# [H] HID: core: ensure the allocated report buffer can contain the reserved report ID

## Summary
Severity: High
Advisory: CVE-2025-38495
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38495
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: core: ensure the allocated report buffer can contain the reserved report ID

When the report ID is not used, the low level transport drivers expect
the first byte to be 0. However, currently the allocated buffer not
account for that extra byte, meaning that instead of having 8 guaranteed
bytes for implement to be working, we only have 7.

## References
- https://git.kernel.org/stable/c/4f15ee98304b96e164ff2340e1dfd6181c3f42aa
- https://git.kernel.org/stable/c/7228e36c7875e4b035374cf68ca5e44dffa596b2
- https://git.kernel.org/stable/c/7fa83d0043370003e9a0b46ab7ae8f53b00fab06
- https://git.kernel.org/stable/c/9f2892f7233a8f1320fe671d0f95f122191bfbcd
- https://git.kernel.org/stable/c/a262370f385e53ff7470efdcdaf40468e5756717
- https://git.kernel.org/stable/c/a47d9d9895bad9ce0e840a39836f19ca0b2a343a
- https://git.kernel.org/stable/c/d3ed1d84a84538a39b3eb2055d6a97a936c108f2
- https://git.kernel.org/stable/c/fcda39a9c5b834346088c14b1374336b079466c1
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38495.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38495
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
