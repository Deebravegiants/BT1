# [M] CVE-2021-46937

## Summary
Severity: Medium
Advisory: CVE-2021-46937
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46937
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/damon/dbgfs: fix 'struct pid' leaks in 'dbgfs_target_ids_write()'

DAMON debugfs interface increases the reference counts of 'struct pid's
for targets from the 'target_ids' file write callback
('dbgfs_target_ids_write()'), but decreases the counts only in DAMON
monitoring termination callback ('dbgfs_before_terminate()').

Therefore, when 'target_ids' file is repeatedly written without DAMON
monitoring start/termination, the reference count is not decreased and
therefore memory for the 'struct pid' cannot be freed.  This commit
fixes this issue by decreasing the reference counts when 'target_ids' is
written.

## References
- https://git.kernel.org/stable/c/ebb3f994dd92f8fb4d70c7541091216c1e10cb71
- https://git.kernel.org/stable/c/ffe4a1ba1a82c416a6b3a09d46594f6a885ae141
