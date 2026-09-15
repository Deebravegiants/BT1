# [H] netfilter: nf_conncount: increase the connection clean up limit to 64

## Summary
Severity: High
Advisory: CVE-2026-45860
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45860
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=5.19.0 <6.6.128, >=6.2.0 <6.12.75, >=6.7.0 <6.18.14, >=6.13.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conncount: increase the connection clean up limit to 64

After the optimization to only perform one GC per jiffy, a new problem
was introduced. If more than 8 new connections are tracked per jiffy the
list won't be cleaned up fast enough possibly reaching the limit
wrongly.

In order to prevent this issue, only skip the GC if it was already
triggered during the same jiffy and the increment is lower than the
clean up limit. In addition, increase the clean up limit to 64
connections to avoid triggering GC too often and do more effective GCs.

This has been tested using a HTTP server and several
performance tools while having nft_connlimit/xt_connlimit or OVS limit
configured.

Output of slowhttptest + OVS limit at 52000 connections:

 slow HTTP test status on 340th second:
 initializing:        0
 pending:             432
 connected:           51998
 error:               0
 closed:              0
 service available:   YES

## References
- https://git.kernel.org/stable/c/0792ad077d776c2dcf20f0484e2461ded1b77a24
- https://git.kernel.org/stable/c/0af0812baf2d363176c9b76fc07e33f13aede8db
- https://git.kernel.org/stable/c/13eede458fdf231f1bf96a398feea4ad1553f14c
- https://git.kernel.org/stable/c/21d033e472735ecec677f1ae46d6740b5e47a4f3
- https://git.kernel.org/stable/c/3d0994ed0aa1fc0a2c5e620b765e8defdd021bff
- https://git.kernel.org/stable/c/6e5fa7add3e76da068a478d905be64be8fa4e80a
- https://git.kernel.org/stable/c/a5c9e14e0e8923218ae881d5e78c990c07694966
- https://git.kernel.org/stable/c/fa85432d58c8e74b39333edbf8d28df2985dfc79
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45860.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45860
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
