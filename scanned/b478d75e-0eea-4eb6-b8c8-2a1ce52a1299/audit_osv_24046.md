# [H] net: sched: Fix use after free in red_enqueue()

## Summary
Severity: High
Advisory: CVE-2022-49921
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49921
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <4.9.333, >=4.10.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: Fix use after free in red_enqueue()

We can't use "skb" again after passing it to qdisc_enqueue().  This is
basically identical to commit 2f09707d0c97 ("sch_sfb: Also store skb
len before calling child enqueue").

## References
- https://git.kernel.org/stable/c/170e5317042c302777ed6d59fdb84af9b0219d4e
- https://git.kernel.org/stable/c/52e0429471976785c155bfbf51d80990c6cd46e2
- https://git.kernel.org/stable/c/5960b9081baca85cc7dcb14aec1de85999ea9d36
- https://git.kernel.org/stable/c/795afe0b9bb6c915f0299a8e309936519be01619
- https://git.kernel.org/stable/c/8bdc2acd420c6f3dd1f1c78750ec989f02a1e2b9
- https://git.kernel.org/stable/c/a238cdcf2bdc72207c74375fc8be13ee549ca9db
- https://git.kernel.org/stable/c/e877f8fa49fbccc63cb2df2e9179bddc695b825a
- https://git.kernel.org/stable/c/fc4b50adb400ee5ec527a04073174e8e73a139fa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49921.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49921
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
