# [H] rpmsg: char: Fix use-after-free on probe error path

## Summary
Severity: High
Advisory: CVE-2026-63797
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63797
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.178, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rpmsg: char: Fix use-after-free on probe error path

rpmsg_chrdev_probe() stores the newly allocated eptdev in the default
endpoint's priv pointer before calling rpmsg_chrdev_eptdev_add(). If
rpmsg_chrdev_eptdev_add() then fails, its error path frees eptdev while
the default endpoint may still dispatch callbacks with the stale priv
pointer.

Avoid publishing eptdev through the default endpoint until
rpmsg_chrdev_eptdev_add() succeeds. Messages received before the priv
pointer is published should be ignored by rpmsg_ept_cb(). Flow-control
updates can hit rpmsg_ept_flow_cb() in the same window, so make both
callbacks return success when priv is NULL.

## References
- https://git.kernel.org/stable/c/104d100212396801f1d9d388282f746e23e2bfd6
- https://git.kernel.org/stable/c/1306fc4f76f765727a6d5aefbf08ef0c8f32996f
- https://git.kernel.org/stable/c/1ff3f528e67d20e2b1483dcaba899dc7832b2e6b
- https://git.kernel.org/stable/c/c5ebb06c7e24d531b68707168e04698859d642bc
- https://git.kernel.org/stable/c/ddf13f91ca82c94ef7ad9c41a434a03313f8eb1b
- https://git.kernel.org/stable/c/ff268cd9ccbce6472a0658791b417bf11c31ee39
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63797.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63797
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
