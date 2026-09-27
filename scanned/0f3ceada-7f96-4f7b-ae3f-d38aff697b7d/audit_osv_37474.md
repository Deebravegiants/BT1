# [H] net/sched: sch_netem: fix out-of-bounds access in packet corruption

## Summary
Severity: High
Advisory: CVE-2026-31675
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31675
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: sch_netem: fix out-of-bounds access in packet corruption

In netem_enqueue(), the packet corruption logic uses
get_random_u32_below(skb_headlen(skb)) to select an index for
modifying skb->data. When an AF_PACKET TX_RING sends fully non-linear
packets over an IPIP tunnel, skb_headlen(skb) evaluates to 0.

Passing 0 to get_random_u32_below() takes the variable-ceil slow path
which returns an unconstrained 32-bit random integer. Using this
unconstrained value as an offset into skb->data results in an
out-of-bounds memory access.

Fix this by verifying skb_headlen(skb) is non-zero before attempting
to corrupt the linear data area. Fully non-linear packets will silently
bypass the corruption logic.

## References
- https://git.kernel.org/stable/c/13a66ca1e235d4bcd53d12d4c68490cad7f8e46f
- https://git.kernel.org/stable/c/3a2999704ac36cfb4041fed3652d26a3373e8d12
- https://git.kernel.org/stable/c/4fd258e281fa8bc15e9ce2c7691941537e9258ad
- https://git.kernel.org/stable/c/a14b56863348686dd0387eea8ce66b85cf455908
- https://git.kernel.org/stable/c/d64cb81dcbd54927515a7f65e5e24affdc73c14b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31675.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31675
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
