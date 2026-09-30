# [M] tracing/osnoise: Fix null-ptr-deref in bitmap_parselist()

## Summary
Severity: Medium
Advisory: CVE-2025-39887
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39887
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing/osnoise: Fix null-ptr-deref in bitmap_parselist()

A crash was observed with the following output:

BUG: kernel NULL pointer dereference, address: 0000000000000010
Oops: Oops: 0000 [#1] SMP NOPTI
CPU: 2 UID: 0 PID: 92 Comm: osnoise_cpus Not tainted 6.17.0-rc4-00201-gd69eb204c255 #138 PREEMPT(voluntary)
RIP: 0010:bitmap_parselist+0x53/0x3e0
Call Trace:
 <TASK>
 osnoise_cpus_write+0x7a/0x190
 vfs_write+0xf8/0x410
 ? do_sys_openat2+0x88/0xd0
 ksys_write+0x60/0xd0
 do_syscall_64+0xa4/0x260
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
 </TASK>

This issue can be reproduced by below code:

fd=open("/sys/kernel/debug/tracing/osnoise/cpus", O_WRONLY);
write(fd, "0-2", 0);

When user pass 'count=0' to osnoise_cpus_write(), kmalloc() will return
ZERO_SIZE_PTR (16) and cpulist_parse() treat it as a normal value, which
trigger the null pointer dereference. Add check for the parameter 'count'.

## References
- https://git.kernel.org/stable/c/c1628c00c4351dd0727ef7f670694f68d9e663d8
- https://git.kernel.org/stable/c/e33228a2cc7ff706ca88533464e8a3b525b961ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39887.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
