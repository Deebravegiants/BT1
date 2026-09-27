# [H] net: atm: fix use after free in lec_send()

## Summary
Severity: High
Advisory: CVE-2025-22004
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-22004
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: atm: fix use after free in lec_send()

The ->send() operation frees skb so save the length before calling
->send() to avoid a use after free.

## References
- https://git.kernel.org/stable/c/326223182e4703cde99fdbd36d07d0b3de9980fb
- https://git.kernel.org/stable/c/50e288097c2c6e5f374ae079394436fc29d1e88e
- https://git.kernel.org/stable/c/51e8be9578a2e74f9983d8fd8de8cafed191f30c
- https://git.kernel.org/stable/c/82d9084a97892de1ee4881eb5c17911fcd9be6f6
- https://git.kernel.org/stable/c/8cd90c7db08f32829bfa1b5b2b11fbc542afbab7
- https://git.kernel.org/stable/c/9566f6ee13b17a15d0a47667ad1b1893c539f730
- https://git.kernel.org/stable/c/f3009d0d6ab78053117f8857b921a8237f4d17b3
- https://git.kernel.org/stable/c/f3271f7548385e0096739965961c7cbf7e6b4762
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22004.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22004
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
