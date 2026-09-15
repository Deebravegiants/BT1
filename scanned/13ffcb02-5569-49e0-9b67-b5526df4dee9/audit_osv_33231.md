# [M] can: j1939: implement NETDEV_UNREGISTER notification handler

## Summary
Severity: Medium
Advisory: CVE-2025-39925
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39925
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.15.220, >=5.16.0 <6.1.187, >=6.2.0 <6.6.156, >=6.7.0 <6.12.108, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: j1939: implement NETDEV_UNREGISTER notification handler

syzbot is reporting

  unregister_netdevice: waiting for vcan0 to become free. Usage count = 2

problem, for j1939 protocol did not have NETDEV_UNREGISTER notification
handler for undoing changes made by j1939_sk_bind().

Commit 25fe97cb7620 ("can: j1939: move j1939_priv_put() into sk_destruct
callback") expects that a call to j1939_priv_put() can be unconditionally
delayed until j1939_sk_sock_destruct() is called. But we need to call
j1939_priv_put() against an extra ref held by j1939_sk_bind() call
(as a part of undoing changes made by j1939_sk_bind()) as soon as
NETDEV_UNREGISTER notification fires (i.e. before j1939_sk_sock_destruct()
is called via j1939_sk_release()). Otherwise, the extra ref on "struct
j1939_priv" held by j1939_sk_bind() call prevents "struct net_device" from
dropping the usage count to 1; making it impossible for
unregister_netdevice() to continue.

[mkl: remove space in front of label]

## References
- https://git.kernel.org/stable/c/2c88069fac2c792e228e6a4ae71c9b9b5b9a87a6
- https://git.kernel.org/stable/c/479d8a2aedcc1db16f14c1a8a9c74b5bdf18b9ac
- https://git.kernel.org/stable/c/4e154cb5e7681c2910e2dfa09f05e3469e333745
- https://git.kernel.org/stable/c/76957b618ce729c3bd1e782fbc9d9991af653925
- https://git.kernel.org/stable/c/7fcbe5b2c6a4b5407bf2241fdb71e0a390f6ab9a
- https://git.kernel.org/stable/c/da9e8f429139928570407e8f90559b5d46c20262
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39925.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
