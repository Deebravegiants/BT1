# [M] CVE-2021-47555

## Summary
Severity: Medium
Advisory: CVE-2021-47555
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47555
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: vlan: fix underflow for the real_dev refcnt

Inject error before dev_hold(real_dev) in register_vlan_dev(),
and execute the following testcase:

ip link add dev dummy1 type dummy
ip link add name dummy1.100 link dummy1 type vlan id 100
ip link del dev dummy1

When the dummy netdevice is removed, we will get a WARNING as following:

=======================================================================
refcount_t: decrement hit 0; leaking memory.
WARNING: CPU: 2 PID: 0 at lib/refcount.c:31 refcount_warn_saturate+0xbf/0x1e0

and an endless loop of:

=======================================================================
unregister_netdevice: waiting for dummy1 to become free. Usage count = -1073741824

That is because dev_put(real_dev) in vlan_dev_free() be called without
dev_hold(real_dev) in register_vlan_dev(). It makes the refcnt of real_dev
underflow.

Move the dev_hold(real_dev) to vlan_dev_init() which is the call-back of
ndo_init(). That makes dev_hold() and dev_put() for vlan's real_dev
symmetrical.

## References
- https://git.kernel.org/stable/c/01d9cc2dea3fde3bad6d27f464eff463496e2b00
- https://git.kernel.org/stable/c/5e44178864b38dd70b877985abd7d86fdb95f27d
- https://git.kernel.org/stable/c/6e800ee43218a56acc93676bbb3d93b74779e555
- https://git.kernel.org/stable/c/f7fc72a508cf115c273a7a29350069def1041890
