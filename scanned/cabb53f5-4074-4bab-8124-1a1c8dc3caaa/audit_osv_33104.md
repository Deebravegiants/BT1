# [H] tracing: Limit access to parser->buffer when trace_get_user failed

## Summary
Severity: High
Advisory: CVE-2025-39683
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39683
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.241, >=5.11.0 <5.15.190, >=5.13.0 <6.1.149, >=5.16.0 <6.6.103, >=6.2.0 <6.12.44, >=6.7.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Limit access to parser->buffer when trace_get_user failed

When the length of the string written to set_ftrace_filter exceeds
FTRACE_BUFF_MAX, the following KASAN alarm will be triggered:

BUG: KASAN: slab-out-of-bounds in strsep+0x18c/0x1b0
Read of size 1 at addr ffff0000d00bd5ba by task ash/165

CPU: 1 UID: 0 PID: 165 Comm: ash Not tainted 6.16.0-g6bcdbd62bd56-dirty
Hardware name: linux,dummy-virt (DT)
Call trace:
 show_stack+0x34/0x50 (C)
 dump_stack_lvl+0xa0/0x158
 print_address_description.constprop.0+0x88/0x398
 print_report+0xb0/0x280
 kasan_report+0xa4/0xf0
 __asan_report_load1_noabort+0x20/0x30
 strsep+0x18c/0x1b0
 ftrace_process_regex.isra.0+0x100/0x2d8
 ftrace_regex_release+0x484/0x618
 __fput+0x364/0xa58
 ____fput+0x28/0x40
 task_work_run+0x154/0x278
 do_notify_resume+0x1f0/0x220
 el0_svc+0xec/0xf0
 el0t_64_sync_handler+0xa0/0xe8
 el0t_64_sync+0x1ac/0x1b0

The reason is that trace_get_user will fail when processing a string
longer than FTRACE_BUFF_MAX, but not set the end of parser->buffer to 0.
Then an OOB access will be triggered in ftrace_regex_release->
ftrace_process_regex->strsep->strpbrk. We can solve this problem by
limiting access to parser->buffer when trace_get_user failed.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/3079517a5ba80901fe828a06998da64b9b8749be
- https://git.kernel.org/stable/c/418b448e1d7470da9d4d4797f71782595ee69c49
- https://git.kernel.org/stable/c/41b838420457802f21918df66764b6fbf829d330
- https://git.kernel.org/stable/c/58ff8064cb4c7eddac4da1a59da039ead586950a
- https://git.kernel.org/stable/c/6a909ea83f226803ea0e718f6e88613df9234d58
- https://git.kernel.org/stable/c/b842ef39c2ad6156c13afdec25ecc6792a9b67b9
- https://git.kernel.org/stable/c/d0c68045b8b0f3737ed7bd6b8c83b7887014adee
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39683.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39683
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
