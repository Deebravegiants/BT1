# [H] CVE-2021-47459

## Summary
Severity: High
Advisory: CVE-2021-47459
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47459
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: j1939: j1939_netdev_start(): fix UAF for rx_kref of j1939_priv

It will trigger UAF for rx_kref of j1939_priv as following.

        cpu0                                    cpu1
j1939_sk_bind(socket0, ndev0, ...)
j1939_netdev_start
                                        j1939_sk_bind(socket1, ndev0, ...)
                                        j1939_netdev_start
j1939_priv_set
                                        j1939_priv_get_by_ndev_locked
j1939_jsk_add
.....
j1939_netdev_stop
kref_put_lock(&priv->rx_kref, ...)
                                        kref_get(&priv->rx_kref, ...)
                                        REFCOUNT_WARN("addition on 0;...")

====================================================
refcount_t: addition on 0; use-after-free.
WARNING: CPU: 1 PID: 20874 at lib/refcount.c:25 refcount_warn_saturate+0x169/0x1e0
RIP: 0010:refcount_warn_saturate+0x169/0x1e0
Call Trace:
 j1939_netdev_start+0x68b/0x920
 j1939_sk_bind+0x426/0xeb0
 ? security_socket_bind+0x83/0xb0

The rx_kref's kref_get() and kref_put() should use j1939_netdev_lock to
protect.

## References
- https://git.kernel.org/stable/c/6e8811707e2df0c6ba920f0cad3a3bca7b42132f
- https://git.kernel.org/stable/c/864e77771a24c877aaf53aee019f78619cbcd668
- https://git.kernel.org/stable/c/a0e47d2833b4f65e6c799f28c6b636d36b8b936d
- https://git.kernel.org/stable/c/d9d52a3ebd284882f5562c88e55991add5d01586
