# [H] vhost: Take a reference on the task in struct vhost_task.

## Summary
Severity: High
Advisory: CVE-2025-40024
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-24
Source: https://osv.dev/vulnerability/CVE-2025-40024
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost: Take a reference on the task in struct vhost_task.

vhost_task_create() creates a task and keeps a reference to its
task_struct. That task may exit early via a signal and its task_struct
will be released.
A pending vhost_task_wake() will then attempt to wake the task and
access a task_struct which is no longer there.

Acquire a reference on the task_struct while creating the thread and
release the reference while the struct vhost_task itself is removed.
If the task exits early due to a signal, then the vhost_task_wake() will
still access a valid task_struct. The wake is safe and will be skipped
in this case.

## References
- https://git.kernel.org/stable/c/7ce635b3d3aba43296b62b5a2d97c008bc51cbd2
- https://git.kernel.org/stable/c/82a1463c968b1a6ae598a4f2fcef17b71bb7d3a0
- https://git.kernel.org/stable/c/afe16653e05db07d658b55245c7a2e0603f136c0
- https://git.kernel.org/stable/c/d2be773a92874a070215b51b730cb2b1eaa8fae2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40024.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40024
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
