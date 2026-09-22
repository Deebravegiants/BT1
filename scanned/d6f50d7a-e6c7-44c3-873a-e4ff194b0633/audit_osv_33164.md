# [M] trace/fgraph: Fix the warning caused by missing unregister notifier

## Summary
Severity: Medium
Advisory: CVE-2025-39829
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39829
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

trace/fgraph: Fix the warning caused by missing unregister notifier

This warning was triggered during testing on v6.16:

notifier callback ftrace_suspend_notifier_call already registered
WARNING: CPU: 2 PID: 86 at kernel/notifier.c:23 notifier_chain_register+0x44/0xb0
...
Call Trace:
 <TASK>
 blocking_notifier_chain_register+0x34/0x60
 register_ftrace_graph+0x330/0x410
 ftrace_profile_write+0x1e9/0x340
 vfs_write+0xf8/0x420
 ? filp_flush+0x8a/0xa0
 ? filp_close+0x1f/0x30
 ? do_dup2+0xaf/0x160
 ksys_write+0x65/0xe0
 do_syscall_64+0xa4/0x260
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

When writing to the function_profile_enabled interface, the notifier was
not unregistered after start_graph_tracing failed, causing a warning the
next time function_profile_enabled was written.

Fixed by adding unregister_pm_notifier in the exception path.

## References
- https://git.kernel.org/stable/c/000aa47a51233fd38a629b029478e0278e1e9fbe
- https://git.kernel.org/stable/c/2a2deb9f8df70480050351ac27041f19bb9e718b
- https://git.kernel.org/stable/c/edede7a6dcd7435395cf757d053974aaab6ab1c2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39829.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39829
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
