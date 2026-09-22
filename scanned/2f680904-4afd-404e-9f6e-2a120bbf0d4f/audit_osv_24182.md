# [H] Bluetooth: L2CAP: Fix user-after-free

## Summary
Severity: High
Advisory: CVE-2022-50386
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50386
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: Fix user-after-free

This uses l2cap_chan_hold_unless_zero() after calling
__l2cap_get_chan_blah() to prevent the following trace:

Bluetooth: l2cap_core.c:static void l2cap_chan_destroy(struct kref
*kref)
Bluetooth: chan 0000000023c4974d
Bluetooth: parent 00000000ae861c08
==================================================================
BUG: KASAN: use-after-free in __mutex_waiter_is_first
kernel/locking/mutex.c:191 [inline]
BUG: KASAN: use-after-free in __mutex_lock_common
kernel/locking/mutex.c:671 [inline]
BUG: KASAN: use-after-free in __mutex_lock+0x278/0x400
kernel/locking/mutex.c:729
Read of size 8 at addr ffff888006a49b08 by task kworker/u3:2/389

## References
- https://git.kernel.org/stable/c/0c108cf3ad386e0084277093b55a351c49e0be27
- https://git.kernel.org/stable/c/11e40d6c0823f699d8ad501e48d1c3ae4be386cd
- https://git.kernel.org/stable/c/15fc21695eb606bdc5d483b92118ee42610a952d
- https://git.kernel.org/stable/c/35fcbc4243aad7e7d020b7c1dfb14bb888b20a4f
- https://git.kernel.org/stable/c/6ffde6e03085874ae22263ff4cef4869f797e84f
- https://git.kernel.org/stable/c/7d6f9cb24d2b2f6b6370eac074e2e6b1bafdad45
- https://git.kernel.org/stable/c/843fc4e386dd84b806a7f07fb062d8c3a44e5364
- https://git.kernel.org/stable/c/d1e894f950ad48897d1a7cb05909ea29d8c3810e
- https://git.kernel.org/stable/c/d91fc2836562f299f34e361e089e9fe154da4f73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50386.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50386
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
