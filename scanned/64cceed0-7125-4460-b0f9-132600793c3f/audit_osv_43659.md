# [H] Bluetooth: L2CAP: fix UAF in l2cap_le_connect_rsp

## Summary
Severity: High
Advisory: CVE-2026-74540
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74540
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: fix UAF in l2cap_le_connect_rsp

l2cap_le_connect_rsp() obtains a channel via
__l2cap_get_chan_by_ident() but neither holds a reference nor uses
l2cap_chan_hold_unless_zero() before locking and operating on it.
A concurrent l2cap_chan_del() triggered by a remote disconnect can
free the channel between the lookup and l2cap_chan_lock(), causing
a use-after-free.

The BR/EDR counterpart l2cap_connect_rsp() and the sibling handler
l2cap_le_command_rej() already use l2cap_chan_hold_unless_zero()
to safely hold a reference, but l2cap_le_connect_rsp() was left
unprotected.

Fix by adding l2cap_chan_hold_unless_zero() after the ident lookup
and l2cap_chan_put() on the exit path, consistent with other L2CAP
response handlers.

## References
- https://git.kernel.org/stable/c/09f447accc2570751e7d17f0dc0788b40d3edade
- https://git.kernel.org/stable/c/15d6c2367217a6a20b1abae9f38ded716bf620f1
- https://git.kernel.org/stable/c/1818180fe12d6cec7a437bc59cde8efdf6b10250
- https://git.kernel.org/stable/c/522b730c62c53a1981604fd73524697fd347830d
- https://git.kernel.org/stable/c/58e3c5289ad230a7e24ae4b0c7b43f5ee6e32136
- https://git.kernel.org/stable/c/8325eafb38c3dee5af329266393763693d17381b
- https://git.kernel.org/stable/c/c4740e7f23ff9a8210198d8b4703259e21b9f69d
- https://git.kernel.org/stable/c/fd4c1e301bdec60a40728ea37de531cbccda501a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74540.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74540
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
