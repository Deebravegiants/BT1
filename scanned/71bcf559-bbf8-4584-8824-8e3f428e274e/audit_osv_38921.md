# [H] eventpoll: defer struct eventpoll free to RCU grace period

## Summary
Severity: High
Advisory: CVE-2026-43074
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43074
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

eventpoll: defer struct eventpoll free to RCU grace period

In certain situations, ep_free() in eventpoll.c will kfree the epi->ep
eventpoll struct while it still being used by another concurrent thread.
Defer the kfree() to an RCU callback to prevent UAF.

## References
- https://git.kernel.org/stable/c/07712db80857d5d09ae08f3df85a708ecfc3b61f
- https://git.kernel.org/stable/c/5b1173b165421561db29f30afc7e97d940a398a9
- https://git.kernel.org/stable/c/7e8083f5eeedab0f460063b9c2c14c9a4e71a427
- https://git.kernel.org/stable/c/902120be4f44947df6311002addc7faf69bdbff1
- https://git.kernel.org/stable/c/a6566cd33f6f967a7651ebf2ce0dd31572e319cf
- https://git.kernel.org/stable/c/a6d57084372161f86660bc4607784420e00efe2c
- https://git.kernel.org/stable/c/ae0bb9c1fb7c2594519aeeb096cf2c3b7837b322
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43074.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43074
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
