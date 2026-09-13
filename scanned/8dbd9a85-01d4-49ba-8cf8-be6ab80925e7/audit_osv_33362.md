# [H] kernel/sys.c: fix the racy usage of task_lock(tsk->group_leader) in sys_prlimit64() paths

## Summary
Severity: High
Advisory: CVE-2025-40201
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40201
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

kernel/sys.c: fix the racy usage of task_lock(tsk->group_leader) in sys_prlimit64() paths

The usage of task_lock(tsk->group_leader) in sys_prlimit64()->do_prlimit()
path is very broken.

sys_prlimit64() does get_task_struct(tsk) but this only protects task_struct
itself. If tsk != current and tsk is not a leader, this process can exit/exec
and task_lock(tsk->group_leader) may use the already freed task_struct.

Another problem is that sys_prlimit64() can race with mt-exec which changes
->group_leader. In this case do_prlimit() may take the wrong lock, or (worse)
->group_leader may change between task_lock() and task_unlock().

Change sys_prlimit64() to take tasklist_lock when necessary. This is not
nice, but I don't see a better fix for -stable.

## References
- https://git.kernel.org/stable/c/132f827e7bac7373e1522e89709d70b43cae5342
- https://git.kernel.org/stable/c/19b45c84bd9fd42fa97ff80c6350d604cb871c75
- https://git.kernel.org/stable/c/1bc0d9315ef5296abb2c9fd840336255850ded18
- https://git.kernel.org/stable/c/6796412decd2d8de8ec708213bbc958fab72f143
- https://git.kernel.org/stable/c/a15f37a40145c986cdf289a4b88390f35efdecc4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40201.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
