# [H] net: sched: fix use-after-free in taprio_change()

## Summary
Severity: High
Advisory: CVE-2024-50127
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50127
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: fix use-after-free in taprio_change()

In 'taprio_change()', 'admin' pointer may become dangling due to sched
switch / removal caused by 'advance_sched()', and critical section
protected by 'q->current_entry_lock' is too small to prevent from such
a scenario (which causes use-after-free detected by KASAN). Fix this
by prefer 'rcu_replace_pointer()' over 'rcu_assign_pointer()' to update
'admin' immediately before an attempt to schedule freeing.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0d4c0d2844e4eac3aed647f948fd7e60eea56a61
- https://git.kernel.org/stable/c/2240f9376f20f8b6463232b4ca7292569217237f
- https://git.kernel.org/stable/c/2f868ce6013548a713c431c679ef73747a66fcf3
- https://git.kernel.org/stable/c/8a283a19026aaae8a773fd8061263cfa315b127f
- https://git.kernel.org/stable/c/999612996df28d81f163dad530d7f8026e03aec6
- https://git.kernel.org/stable/c/f504465970aebb2467da548f7c1efbbf36d0f44b
- https://git.kernel.org/stable/c/fe371f084073e8672a2d7d46b335c3c060d1e301
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50127.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50127
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
