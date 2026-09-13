# [H] rbd: avoid use-after-free in do_rbd_add() when rbd_dev_create() fails

## Summary
Severity: High
Advisory: CVE-2023-53307
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53307
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rbd: avoid use-after-free in do_rbd_add() when rbd_dev_create() fails

If getting an ID or setting up a work queue in rbd_dev_create() fails,
use-after-free on rbd_dev->rbd_client, rbd_dev->spec and rbd_dev->opts
is triggered in do_rbd_add().  The root cause is that the ownership of
these structures is transfered to rbd_dev prematurely and they all end
up getting freed when rbd_dev_create() calls rbd_dev_free() prior to
returning to do_rbd_add().

Found by Linux Verification Center (linuxtesting.org) with SVACE, an
incomplete patch submitted by Natalia Petrova <n.petrova@fintech.ru>.

## References
- https://git.kernel.org/stable/c/71da2a151ed1adb0aea4252b16d81b53012e7afd
- https://git.kernel.org/stable/c/9787b328c42c13c4f31e7d5042c4e877e9344068
- https://git.kernel.org/stable/c/a73783e4e0c4d1507794da211eeca75498544dff
- https://git.kernel.org/stable/c/ae16346078b1189aee934afd872d9f3d0a682c33
- https://git.kernel.org/stable/c/cc8c0dd2984503ed09efa37bcafcef3d3da104e8
- https://git.kernel.org/stable/c/e3cbb4d60764295992c95344f2d779439e8b34ce
- https://git.kernel.org/stable/c/f7c4d9b133c7a04ca619355574e96b6abf209fba
- https://git.kernel.org/stable/c/faa7b683e436664fff5648426950718277831348
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53307.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53307
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
