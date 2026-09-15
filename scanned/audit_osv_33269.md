# [H] futex: Use correct exit on failure from futex_hash_allocate_default()

## Summary
Severity: High
Advisory: CVE-2025-39976
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39976
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

futex: Use correct exit on failure from futex_hash_allocate_default()

copy_process() uses the wrong error exit path from futex_hash_allocate_default().
After exiting from futex_hash_allocate_default(), neither tasklist_lock
nor siglock has been acquired. The exit label bad_fork_core_free unlocks
both of these locks which is wrong.

The next exit label, bad_fork_cancel_cgroup, is the correct exit.
sched_cgroup_fork() did not allocate any resources that need to freed.

Use bad_fork_cancel_cgroup on error exit from futex_hash_allocate_default().

## References
- https://git.kernel.org/stable/c/4ec3c15462b9f44562f45723a92e2807746ba7d1
- https://git.kernel.org/stable/c/f1635765cd0fdbf27b04d9a50be91a01b5adda13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39976.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39976
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
