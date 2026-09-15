# [H] netfilter: nf_tables: release flowtable after rcu grace period on error

## Summary
Severity: High
Advisory: CVE-2026-23392
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23392
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: release flowtable after rcu grace period on error

Call synchronize_rcu() after unregistering the hooks from error path,
since a hook that already refers to this flowtable can be already
registered, exposing this flowtable to packet path and nfnetlink_hook
control plane.

This error path is rare, it should only happen by reaching the maximum
number hooks or by failing to set up to hardware offload, just call
synchronize_rcu().

There is a check for already used device hooks by different flowtable
that could result in EEXIST at this late stage. The hook parser can be
updated to perform this check earlier to this error path really becomes
rarely exercised.

Uncovered by KASAN reported as use-after-free from nfnetlink_hook path
when dumping hooks.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/7e3955b282eae20d61c75e499c75eade51c20060
- https://git.kernel.org/stable/c/adee3436ccd29f1e514c028899e400cbc6d84065
- https://git.kernel.org/stable/c/c8092edb9a11f20f95ccceeb9422b7dd0df337bd
- https://git.kernel.org/stable/c/d2632de96ccb066e0131ad1494241b9c281c60b8
- https://git.kernel.org/stable/c/d73f4b53aaaea4c95f245e491aa5eeb8a21874ce
- https://git.kernel.org/stable/c/e78a2dcc7cfb87b64a631441ca7681492b347ef6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23392.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23392
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
