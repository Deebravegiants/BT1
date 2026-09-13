# [H] CVE-2021-47088

## Summary
Severity: High
Advisory: CVE-2021-47088
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47088
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/damon/dbgfs: protect targets destructions with kdamond_lock

DAMON debugfs interface iterates current monitoring targets in
'dbgfs_target_ids_read()' while holding the corresponding
'kdamond_lock'.  However, it also destructs the monitoring targets in
'dbgfs_before_terminate()' without holding the lock.  This can result in
a use_after_free bug.  This commit avoids the race by protecting the
destruction with the corresponding 'kdamond_lock'.

## References
- https://git.kernel.org/stable/c/330c6117a82c16a9a365a51cec5c9ab30b13245c
- https://git.kernel.org/stable/c/34796417964b8d0aef45a99cf6c2d20cebe33733
