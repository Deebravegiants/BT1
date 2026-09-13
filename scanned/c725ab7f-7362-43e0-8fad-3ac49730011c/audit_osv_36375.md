# [H] net/sched: Only allow act_ct to bind to clsact/ingress qdiscs and shared blocks

## Summary
Severity: High
Advisory: CVE-2026-23270
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23270
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.8.0 <6.18.18, >=6.13.0 <6.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: Only allow act_ct to bind to clsact/ingress qdiscs and shared blocks

As Paolo said earlier [1]:

"Since the blamed commit below, classify can return TC_ACT_CONSUMED while
the current skb being held by the defragmentation engine. As reported by
GangMin Kim, if such packet is that may cause a UaF when the defrag engine
later on tries to tuch again such packet."

act_ct was never meant to be used in the egress path, however some users
are attaching it to egress today [2]. Attempting to reach a middle
ground, we noticed that, while most qdiscs are not handling
TC_ACT_CONSUMED, clsact/ingress qdiscs are. With that in mind, we
address the issue by only allowing act_ct to bind to clsact/ingress
qdiscs and shared blocks. That way it's still possible to attach act_ct to
egress (albeit only with clsact).

[1] https://lore.kernel.org/netdev/674b8cbfc385c6f37fb29a1de08d8fe5c2b0fbee.1771321118.git.pabeni@redhat.com/
[2] https://lore.kernel.org/netdev/cc6bfb4a-4a2b-42d8-b9ce-7ef6644fb22b@ovn.org/

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/11cb63b0d1a0685e0831ae3c77223e002ef18189
- https://git.kernel.org/stable/c/380ad8b7c65ea7aa10ef2258297079ed5ac1f5b6
- https://git.kernel.org/stable/c/524ce8b4ea8f64900b6c52b6a28df74f6bc0801e
- https://git.kernel.org/stable/c/5a110ddcc99bda77a28598b3555fe009eaab3828
- https://git.kernel.org/stable/c/9deda0fcda5c1f388c5e279541850b71a2ccfcf4
- https://git.kernel.org/stable/c/bc4e5bb529823a09f02dbe96169de679a9db26e0
- https://git.kernel.org/stable/c/fb3c380a54e33d1fd272cc342faa906d787d7ef1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23270.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
