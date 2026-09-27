# [H] atl1c: Work around the DMA RX overflow issue

## Summary
Severity: High
Advisory: CVE-2023-52834
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52834
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

atl1c: Work around the DMA RX overflow issue

This is based on alx driver commit 881d0327db37 ("net: alx: Work around
the DMA RX overflow issue").

The alx and atl1c drivers had RX overflow error which was why a custom
allocator was created to avoid certain addresses. The simpler workaround
then created for alx driver, but not for atl1c due to lack of tester.

Instead of using a custom allocator, check the allocated skb address and
use skb_reserve() to move away from problematic 0x...fc0 address.

Tested on AR8131 on Acer 4540.

## References
- https://git.kernel.org/stable/c/32f08b7b430ee01ec47d730f961a3306c1c7b6fb
- https://git.kernel.org/stable/c/54a6152da4993ec8e4b53dc3cf577f5a2c829afa
- https://git.kernel.org/stable/c/57e44ff9c2c9747b2b1a53556810b0e5192655d6
- https://git.kernel.org/stable/c/86565682e9053e5deb128193ea9e88531bbae9cf
- https://git.kernel.org/stable/c/c29a89b23f67ee592f4dee61f9d7efbf86d60315
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52834.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52834
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
