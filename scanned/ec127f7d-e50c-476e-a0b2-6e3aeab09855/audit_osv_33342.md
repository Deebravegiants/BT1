# [H] ipv6: use RCU in ip6_output()

## Summary
Severity: High
Advisory: CVE-2025-40158
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40158
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: use RCU in ip6_output()

Use RCU in ip6_output() in order to use dst_dev_rcu() to prevent
possible UAF.

We can remove rcu_read_lock()/rcu_read_unlock() pairs
from ip6_finish_output2().

## References
- https://git.kernel.org/stable/c/0393f85c3241c19ba8550f04a812e7d19f6b3082
- https://git.kernel.org/stable/c/11709573cc4e48dc34c80fc7ab9ce5b159e29695
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40158.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40158
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
