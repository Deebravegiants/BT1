# [H] net: fix fanout UAF in packet_release() via NETDEV_UP race

## Summary
Severity: High
Advisory: CVE-2026-31504
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31504
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fix fanout UAF in packet_release() via NETDEV_UP race

`packet_release()` has a race window where `NETDEV_UP` can re-register a
socket into a fanout group's `arr[]` array. The re-registration is not
cleaned up by `fanout_release()`, leaving a dangling pointer in the fanout
array.
`packet_release()` does NOT zero `po->num` in its `bind_lock` section.
After releasing `bind_lock`, `po->num` is still non-zero and `po->ifindex`
still matches the bound device. A concurrent `packet_notifier(NETDEV_UP)`
that already found the socket in `sklist` can re-register the hook.
For fanout sockets, this re-registration calls `__fanout_link(sk, po)`
which adds the socket back into `f->arr[]` and increments `f->num_members`,
but does NOT increment `f->sk_ref`.

The fix sets `po->num` to zero in `packet_release` while `bind_lock` is
held to prevent NETDEV_UP from linking, preventing the race window.

This bug was found following an additional audit with Claude Code based
on CVE-2025-38617.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1b4c03f8892d955385c202009af7485364731bb9
- https://git.kernel.org/stable/c/42156f93d123436f2a27c468f18c966b7e5db796
- https://git.kernel.org/stable/c/42cfd7898eeed290c9fb73f732af1f7d6b0a703e
- https://git.kernel.org/stable/c/654386baef228c2992dbf604c819e4c7c35fc71b
- https://git.kernel.org/stable/c/75fe6db23705a1d55160081f7b37db9665b1880b
- https://git.kernel.org/stable/c/ceccbfc6de720ad633519a226715989cfb065af1
- https://git.kernel.org/stable/c/d0c7cdc15fdf8c4f91aca1928e52295d175b6ec6
- https://git.kernel.org/stable/c/ee642b1962caa9aa231c01abbd58bc453ae6b66e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31504.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31504
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
