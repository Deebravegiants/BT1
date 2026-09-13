# [H] 9p/xen: fix release of IRQ

## Summary
Severity: High
Advisory: CVE-2024-56704
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56704
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p/xen: fix release of IRQ

Kernel logs indicate an IRQ was double-freed.

Pass correct device ID during IRQ release.

[Dominique: remove confusing variable reset to 0]

## References
- https://git.kernel.org/stable/c/2bb3ee1bf237557daea1d58007d2e1d4a6502ccf
- https://git.kernel.org/stable/c/4950408793b118cb8075bcee1f033b543fb719fa
- https://git.kernel.org/stable/c/530bc9f03a102fac95b07cda513bfc16ff69e0ee
- https://git.kernel.org/stable/c/692eb06703afc3e24d889d77e94a0e20229f6a4a
- https://git.kernel.org/stable/c/7f5a2ed5c1810661e6b03f5a4ebf17682cdea850
- https://git.kernel.org/stable/c/b9e26059664bd9ebc64a0e8f5216266fc9f84265
- https://git.kernel.org/stable/c/d74b4b297097bd361b8a9abfde9b521ff464ea9c
- https://git.kernel.org/stable/c/d888f5f5d76b2722c267e6bdf51d445d60647b7b
- https://git.kernel.org/stable/c/e43c608f40c065b30964f0a806348062991b802d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56704.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56704
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
