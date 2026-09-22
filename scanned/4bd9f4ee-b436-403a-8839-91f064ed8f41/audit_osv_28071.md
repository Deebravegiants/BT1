# [H] tcp: Fix Use-After-Free in tcp_ao_connect_init

## Summary
Severity: High
Advisory: CVE-2024-27394
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-27394
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix Use-After-Free in tcp_ao_connect_init

Since call_rcu, which is called in the hlist_for_each_entry_rcu traversal
of tcp_ao_connect_init, is not part of the RCU read critical section, it
is possible that the RCU grace period will pass during the traversal and
the key will be free.

To prevent this, it should be changed to hlist_for_each_entry_safe.

## References
- https://git.kernel.org/stable/c/80e679b352c3ce5158f3f778cfb77eb767e586fb
- https://git.kernel.org/stable/c/ca4fb6c6764b3f75b4f5aa81db1536291897ff7f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27394.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27394
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
