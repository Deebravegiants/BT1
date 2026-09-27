# [H] aio: Fix null ptr deref in aio_complete() wakeup

## Summary
Severity: High
Advisory: CVE-2024-35874
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35874
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

aio: Fix null ptr deref in aio_complete() wakeup

list_del_init_careful() needs to be the last access to the wait queue
entry - it effectively unlocks access.

Previously, finish_wait() would see the empty list head and skip taking
the lock, and then we'd return - but the completion path would still
attempt to do the wakeup after the task_struct pointer had been
overwritten.

## References
- https://git.kernel.org/stable/c/9678bcc6234d83759fe091c197f5017a32b468da
- https://git.kernel.org/stable/c/caeb4b0a11b3393e43f7fa8e0a5a18462acc66bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35874.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35874
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
