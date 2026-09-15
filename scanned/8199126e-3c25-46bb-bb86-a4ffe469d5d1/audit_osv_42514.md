# [H] net/packet: avoid fanout hook re-registration after unregister

## Summary
Severity: High
Advisory: CVE-2026-68338
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68338
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/packet: avoid fanout hook re-registration after unregister

packet_set_ring() temporarily detaches a socket from packet delivery while
reconfiguring its ring. It records the previous running state, clears
po->num, unregisters the protocol hook when needed, drops po->bind_lock,
and later restores po->num and re-registers the hook from the saved
was_running value.

That unlocked window can race with NETDEV_UNREGISTER. The notifier can
observe the socket as not running, skip __unregister_prot_hook(), and
invalidate the per-socket binding by setting po->ifindex to -1 and clearing
po->prot_hook.dev. A one-member fanout group can still retain its shared
fanout hook device pointer. When packet_set_ring() resumes, re-registering
solely from the stale was_running state can re-add the fanout hook after
the device has been unregistered.

Treat po->ifindex == -1 as an invalidated binding after reacquiring
po->bind_lock. This is distinct from ifindex 0, the normal
unbound/wildcard state: ifindex -1 marks an existing device binding that
was invalidated when the device was unregistered. Restore po->num as
before, but do not re-register the hook if device unregister already
detached the socket.

## References
- https://git.kernel.org/stable/c/0a052e0808e015e68144a9877e6ef42b952c49fa
- https://git.kernel.org/stable/c/1bc55c29cd85818e9052f17deb287d5a11fb817f
- https://git.kernel.org/stable/c/4628efbdc7affd094181f5263e65c1062e31f15f
- https://git.kernel.org/stable/c/50aff80475abd3533eef4320477037e6fcc6b56e
- https://git.kernel.org/stable/c/80ec024d53a05c60ad1d08968dcf745f10c1665c
- https://git.kernel.org/stable/c/a885387dae7986a55bae5c77a15bdd447f64e9b9
- https://git.kernel.org/stable/c/acb40ebfa5c4d62f84339fcbf713f2a9fd033a71
- https://git.kernel.org/stable/c/c820f4b7f2fa38f8769db0d0cefdd94e2721504d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68338.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68338
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
