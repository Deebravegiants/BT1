# [H] ipv6: prevent possible UaF in addrconf_permanent_addr()

## Summary
Severity: High
Advisory: CVE-2026-43339
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43339
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: prevent possible UaF in addrconf_permanent_addr()

The mentioned helper try to warn the user about an exceptional
condition, but the message is delivered too late, accessing the ipv6
after its possible deletion.

Reorder the statement to avoid the possible UaF; while at it, place the
warning outside the idev->lock as it needs no protection.

## References
- https://git.kernel.org/stable/c/25357b670afb5b517096da783abaa5cc4bf8359e
- https://git.kernel.org/stable/c/2d88ed7fa000e19c2dc0fa31b3a849e3f5bca5c1
- https://git.kernel.org/stable/c/3cd4efb5df72843dfac892d0b3c7a4a8bd926b65
- https://git.kernel.org/stable/c/7bfafa1b0cd582983ebec6bb20f0a435528fe567
- https://git.kernel.org/stable/c/7d9f2f4aabd116ca68fbdab5d8fb8dac74c2ea1e
- https://git.kernel.org/stable/c/bacc7f31085c9820922f00bc7d79756ffa13123a
- https://git.kernel.org/stable/c/eec49a33611f20336b357b3953df44f1a02049e8
- https://git.kernel.org/stable/c/fd63f185979b047fb22a0dfc6bd94d0cab6a6a70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43339.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43339
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
