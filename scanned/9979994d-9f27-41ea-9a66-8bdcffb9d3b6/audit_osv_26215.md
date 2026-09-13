# [H] net: fix possible store tearing in neigh_periodic_work()

## Summary
Severity: High
Advisory: CVE-2023-52522
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52522
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <5.4.258, >=5.5.0 <5.10.198, >=5.11.0 <5.15.135, >=5.16.0 <6.1.57, >=6.2.0 <6.5.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fix possible store tearing in neigh_periodic_work()

While looking at a related syzbot report involving neigh_periodic_work(),
I found that I forgot to add an annotation when deleting an
RCU protected item from a list.

Readers use rcu_deference(*np), we need to use either
rcu_assign_pointer() or WRITE_ONCE() on writer side
to prevent store tearing.

I use rcu_assign_pointer() to have lockdep support,
this was the choice made in neigh_flush_dev().

## References
- https://git.kernel.org/stable/c/147d89ee41434b97043c2dcb17a97dc151859baa
- https://git.kernel.org/stable/c/25563b581ba3a1f263a00e8c9a97f5e7363be6fd
- https://git.kernel.org/stable/c/2ea52a2fb8e87067e26bbab4efb8872639240eb0
- https://git.kernel.org/stable/c/95eabb075a5902f4c0834ab1fb12dc35730c05af
- https://git.kernel.org/stable/c/a75152d233370362eebedb2643592e7c883cc9fc
- https://git.kernel.org/stable/c/f82aac8162871e87027692b36af335a2375d4580
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52522.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52522
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
