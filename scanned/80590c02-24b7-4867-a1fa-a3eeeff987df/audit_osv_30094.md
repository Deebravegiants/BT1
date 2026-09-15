# [H] net: do not delay dst_entries_add() in dst_release()

## Summary
Severity: High
Advisory: CVE-2024-50036
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50036
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: do not delay dst_entries_add() in dst_release()

dst_entries_add() uses per-cpu data that might be freed at netns
dismantle from ip6_route_net_exit() calling dst_entries_destroy()

Before ip6_route_net_exit() can be called, we release all
the dsts associated with this netns, via calls to dst_release(),
which waits an rcu grace period before calling dst_destroy()

dst_entries_add() use in dst_destroy() is racy, because
dst_entries_destroy() could have been called already.

Decrementing the number of dsts must happen sooner.

Notes:

1) in CONFIG_XFRM case, dst_destroy() can call
   dst_release_immediate(child), this might also cause UAF
   if the child does not have DST_NOCOUNT set.
   IPSEC maintainers might take a look and see how to address this.

2) There is also discussion about removing this count of dst,
   which might happen in future kernels.

## References
- https://git.kernel.org/stable/c/3c7c918ec0aa3555372c5a57f18780b7a96c5cfc
- https://git.kernel.org/stable/c/547087307bc19417b4f2bc85ba9664a3e8db5a6a
- https://git.kernel.org/stable/c/a60db84f772fc3a906c6c4072f9207579c41166f
- https://git.kernel.org/stable/c/ac888d58869bb99753e7652be19a151df9ecb35d
- https://git.kernel.org/stable/c/e3915f028b1f1c37e87542e5aadd33728c259d96
- https://git.kernel.org/stable/c/eae7435b48ffc8e9be0ff9cfeae40af479a609dd
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50036.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50036
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
