# [H] netfilter: ipset: fix order of kfree_rcu() and rcu_assign_pointer()

## Summary
Severity: High
Advisory: CVE-2026-72435
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72435
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: fix order of kfree_rcu() and rcu_assign_pointer()

Sashiko pointed out that kfree_rcu() was called before
rcu_assign_pointer() in handling the comment extension.
Fix the order so that rcu_assign_pointer() called first.

## References
- https://git.kernel.org/stable/c/3ca9982a8882470aa0ac4e8bb9a552b181d1efcd
- https://git.kernel.org/stable/c/50b70f56f3baaff46599f59b2d93fa2540120776
- https://git.kernel.org/stable/c/6e98407cb94e035bba98956adc9096a76d8b2a9f
- https://git.kernel.org/stable/c/8087bb360a936a6314d22b567e4b861656943eb6
- https://git.kernel.org/stable/c/93a775fd67f3ef34949a9523bfa69403ee74efdd
- https://git.kernel.org/stable/c/c9787d7c24ffd83019f379455e1b97fb4f0f75eb
- https://git.kernel.org/stable/c/d01b4b471f0fc5c396af62845e972ccf99cee29a
- https://git.kernel.org/stable/c/fcb565966534909377a16be5f7b065db2e25c8b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72435.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72435
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
