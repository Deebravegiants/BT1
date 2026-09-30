# [H] net/smc: avoid early lgr access in smc_clc_wait_msg

## Summary
Severity: High
Advisory: CVE-2026-46027
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46027
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: avoid early lgr access in smc_clc_wait_msg

A CLC decline can be received while the handshake is still in an early
stage, before the connection has been associated with a link group.

The decline handling in smc_clc_wait_msg() updates link-group level sync
state for first-contact declines, but that state only exists after link
group setup has completed. Guard the link-group update accordingly and
keep the per-socket peer diagnosis handling unchanged.

This preserves the existing sync_err handling for established link-group
contexts and avoids touching link-group state before it is available.

## References
- https://git.kernel.org/stable/c/22546729b96fc873b23065dc49e3d73c45cfb874
- https://git.kernel.org/stable/c/257cdf0c5ced9c0fba8aba501d94b0a5fcef2086
- https://git.kernel.org/stable/c/5a8db80f721deee8e916c2cfdee78decda02ce4f
- https://git.kernel.org/stable/c/5eedbfd82c2884e0010fdfb3c9446a6ebcadb691
- https://git.kernel.org/stable/c/6180a296ca65b08a81914805cbc0f78da5f10a1f
- https://git.kernel.org/stable/c/83bcf9228b0501694fb2589ed1d142855a2887f2
- https://git.kernel.org/stable/c/ea0b5d0fe96356dce38f98375a57c52a04e13712
- https://git.kernel.org/stable/c/f0858e1d5624bb120b198f2a8528f97a9b0ae069
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46027.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46027
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
