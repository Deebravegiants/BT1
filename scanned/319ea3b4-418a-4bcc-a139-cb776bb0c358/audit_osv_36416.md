# [H] net: shaper: protect late read accesses to the hierarchy

## Summary
Severity: High
Advisory: CVE-2026-23437
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23437
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: shaper: protect late read accesses to the hierarchy

We look up a netdev during prep of Netlink ops (pre- callbacks)
and take a ref to it. Then later in the body of the callback
we take its lock or RCU which are the actual protections.

This is not proper, a conversion from a ref to a locked netdev
must include a liveness check (a check if the netdev hasn't been
unregistered already). Fix the read cases (those under RCU).
Writes needs a separate change to protect from creating the
hierarchy after flush has already run.

## References
- https://git.kernel.org/stable/c/0f9ea7141f365b4f27226898e62220fb98ef8dc6
- https://git.kernel.org/stable/c/348758ba74e6a348299965b16a97cfb817545cc0
- https://git.kernel.org/stable/c/581eee0890a8bde44f1fb78ad3e70502a897d583
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23437.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23437
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
