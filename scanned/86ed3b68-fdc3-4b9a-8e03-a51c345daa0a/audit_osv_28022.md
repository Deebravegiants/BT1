# [H] interconnect: Don't access req_list while it's being manipulated

## Summary
Severity: High
Advisory: CVE-2024-27005
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27005
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.151, >=5.16.0 <6.1.81, >=6.2.0 <6.6.29, >=6.6.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

interconnect: Don't access req_list while it's being manipulated

The icc_lock mutex was split into separate icc_lock and icc_bw_lock
mutexes in [1] to avoid lockdep splats. However, this didn't adequately
protect access to icc_node::req_list.

The icc_set_bw() function will eventually iterate over req_list while
only holding icc_bw_lock, but req_list can be modified while only
holding icc_lock. This causes races between icc_set_bw(), of_icc_get(),
and icc_put().

Example A:

  CPU0                               CPU1
  ----                               ----
  icc_set_bw(path_a)
    mutex_lock(&icc_bw_lock);
                                     icc_put(path_b)
                                       mutex_lock(&icc_lock);
    aggregate_requests()
      hlist_for_each_entry(r, ...
                                       hlist_del(...
        <r = invalid pointer>

Example B:

  CPU0                               CPU1
  ----                               ----
  icc_set_bw(path_a)
    mutex_lock(&icc_bw_lock);
                                     path_b = of_icc_get()
                                       of_icc_get_by_index()
                                         mutex_lock(&icc_lock);
                                         path_find()
                                           path_init()
    aggregate_requests()
      hlist_for_each_entry(r, ...
                                             hlist_add_head(...
        <r = invalid pointer>

Fix this by ensuring icc_bw_lock is always held before manipulating
icc_node::req_list. The additional places icc_bw_lock is held don't
perform any memory allocations, so we should still be safe from the
original lockdep splats that motivated the separate locks.

[1] commit af42269c3523 ("interconnect: Fix locking for runpm vs reclaim")

## References
- https://git.kernel.org/stable/c/19ec82b3cad1abef2a929262b8c1528f4e0c192d
- https://git.kernel.org/stable/c/4c65507121ea8e0b47fae6d2049c8688390d46b6
- https://git.kernel.org/stable/c/d0d04efa2e367921654b5106cc5c05e3757c2b42
- https://git.kernel.org/stable/c/de1bf25b6d771abdb52d43546cf57ad775fb68a1
- https://git.kernel.org/stable/c/fe549d8e976300d0dd75bd904eb216bed8b145e0
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27005.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27005
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
