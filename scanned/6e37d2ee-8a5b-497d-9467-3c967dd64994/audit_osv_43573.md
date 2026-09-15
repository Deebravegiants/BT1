# [H] OPP: Fix race between OPP addition and lookup

## Summary
Severity: High
Advisory: CVE-2026-74405
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74405
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

OPP: Fix race between OPP addition and lookup

A race exists between dev_pm_opp_add_dynamic() and
dev_pm_opp_find_freq_exact():

  CPU0 (add)                          CPU1 (lookup)
  -------------------------------     ------------------------------
  _opp_add()
    mutex_lock()
    list_add(&new_opp->node, head)
    mutex_unlock()                    _opp_table_find_key()
                                        mutex_lock()
                                        dev_pm_opp_get(opp)
                                          kref_get()
                                        mutex_unlock()
    kref_init(&new_opp->kref)
                                      dev_pm_opp_put()
                                        kref_put_mutex()

The newly added OPP is inserted into the list before its kref is
initialized. A concurrent lookup can find this OPP and increment its
reference count while it is still uninitialized, leading to refcount
corruption and a potential premature free.

Fix this by initializing ->kref and ->opp_table before making the OPP
visible via list_add(). This ensures any concurrent lookup observes a
fully initialized object.

[ Viresh: Updated commit log ]

## References
- https://git.kernel.org/stable/c/46696b0b2123475d7f95909435c09808fc5ffd23
- https://git.kernel.org/stable/c/bb75bd7d9ae7672034f73ce67a57e6ac89bb39e5
- https://git.kernel.org/stable/c/f5e1cc9a284bff2510981643a5bca4bc4c21b81a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74405.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74405
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
