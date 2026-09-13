# [H] netfilter: nf_tables: netlink notifier might race to release objects

## Summary
Severity: High
Advisory: CVE-2022-49920
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49920
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: netlink notifier might race to release objects

commit release path is invoked via call_rcu and it runs lockless to
release the objects after rcu grace period. The netlink notifier handler
might win race to remove objects that the transaction context is still
referencing from the commit release path.

Call rcu_barrier() to ensure pending rcu callbacks run to completion
if the list of transactions to be destroyed is not empty.

## References
- https://git.kernel.org/stable/c/1ffe7100411a8b9015115ce124cd6c9c9da6f8e3
- https://git.kernel.org/stable/c/d4bc8271db21ea9f1c86a1ca4d64999f184d4aae
- https://git.kernel.org/stable/c/e40b7c44d19e327ad8b49a491ef1fa8dcc4566e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49920.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49920
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
