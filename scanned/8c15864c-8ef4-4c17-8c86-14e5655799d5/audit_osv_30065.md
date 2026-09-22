# [H] net/xen-netback: prevent UAF in xenvif_flush_hash()

## Summary
Severity: High
Advisory: CVE-2024-49936
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49936
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.4.290, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/xen-netback: prevent UAF in xenvif_flush_hash()

During the list_for_each_entry_rcu iteration call of xenvif_flush_hash,
kfree_rcu does not exist inside the rcu read critical section, so if
kfree_rcu is called when the rcu grace period ends during the iteration,
UAF occurs when accessing head->next after the entry becomes free.

Therefore, to solve this, you need to change it to list_for_each_entry_safe.

## References
- https://git.kernel.org/stable/c/0fa5e94a1811d68fbffa0725efe6d4ca62c03d12
- https://git.kernel.org/stable/c/143edf098b80669d05245b2f2367dd156a83a2c5
- https://git.kernel.org/stable/c/3c4423b0c4b98213b3438e15061e1d08220e6982
- https://git.kernel.org/stable/c/54d8639af5568fc41c0e274fc3ec9cf86c59fcbb
- https://git.kernel.org/stable/c/a0465723b8581cad27164c9073fd780904cd22d4
- https://git.kernel.org/stable/c/a7f0073fcd12ed7de185ef2c0af9d0fa1ddef22c
- https://git.kernel.org/stable/c/d408889d4b54f5501e4becc4dbbb9065143fbf4e
- https://git.kernel.org/stable/c/efcff6ce7467f01f0753609f420333f3f2ceceda
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49936.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49936
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
