# [H] xfrm: Wait for RCU readers during policy netns exit

## Summary
Severity: High
Advisory: CVE-2026-43091
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43091
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: Wait for RCU readers during policy netns exit

xfrm_policy_fini() frees the policy_bydst hash tables after flushing the
policy work items and deleting all policies, but it does not wait for
concurrent RCU readers to leave their read-side critical sections first.

The policy_bydst tables are published via rcu_assign_pointer() and are
looked up through rcu_dereference_check(), so netns teardown must also
wait for an RCU grace period before freeing the table memory.

Fix this by adding synchronize_rcu() before freeing the policy hash tables.

## References
- https://git.kernel.org/stable/c/069daad4f2ae9c5c108131995529d5f02392c446
- https://git.kernel.org/stable/c/33a3149dd81a1e2f52b80ee1e0fc380b39f3d028
- https://git.kernel.org/stable/c/3733fce2871c9bca9dd18a1a23b1432ea215a094
- https://git.kernel.org/stable/c/438b1f668ad58f46ce699bb48e4698a7839e3f9e
- https://git.kernel.org/stable/c/b66920a3348c0f63ba18365248fa21fbf0b3a937
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43091.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43091
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
