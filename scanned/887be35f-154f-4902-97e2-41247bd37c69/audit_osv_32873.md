# [H] net: atm: fix /proc/net/atm/lec handling

## Summary
Severity: High
Advisory: CVE-2025-38180
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38180
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: atm: fix /proc/net/atm/lec handling

/proc/net/atm/lec must ensure safety against dev_lec[] changes.

It appears it had dev_put() calls without prior dev_hold(),
leading to imbalance and UAF.

## References
- https://git.kernel.org/stable/c/5fe1b23a2f87f43aeeac51e08819cbc6fd808cbc
- https://git.kernel.org/stable/c/9b9aeb3ada44d8abea1e31e4446113f460848ae4
- https://git.kernel.org/stable/c/a5e3a144268899f1a8c445c8a3bfa15873ba85e8
- https://git.kernel.org/stable/c/ca3829c18c8d0ceb656605d3bff6bb3dfb078589
- https://git.kernel.org/stable/c/d03b79f459c7935cff830d98373474f440bd03ae
- https://git.kernel.org/stable/c/e612c4b014f5808fbc6beae21f5ccaca5e76a2f8
- https://git.kernel.org/stable/c/f2d1443b18806640abdb530e88009af7be2588e7
- https://git.kernel.org/stable/c/fcfccf56f4eba7d00aa2d33c7bb1b33083237742
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38180.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38180
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
