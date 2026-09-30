# [H] netfilter: nf_tables: join hook list via splice_list_rcu() in commit phase

## Summary
Severity: High
Advisory: CVE-2026-52988
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52988
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: join hook list via splice_list_rcu() in commit phase

Publish new hooks in the list into the basechain/flowtable using
splice_list_rcu() to ensure netlink dump list traversal via rcu is safe
while concurrent ruleset update is going on.

## References
- https://git.kernel.org/stable/c/1346be9379639c30877083b12747d4eacb83c24f
- https://git.kernel.org/stable/c/a6134e62dba2ea4f760b29d5226907f447c92400
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52988.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
