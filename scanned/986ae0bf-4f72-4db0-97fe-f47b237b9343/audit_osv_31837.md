# [M] net/sched: cls_api: fix error handling causing NULL dereference

## Summary
Severity: Medium
Advisory: CVE-2025-21857
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21857
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: cls_api: fix error handling causing NULL dereference

tcf_exts_miss_cookie_base_alloc() calls xa_alloc_cyclic() which can
return 1 if the allocation succeeded after wrapping. This was treated as
an error, with value 1 returned to caller tcf_exts_init_ex() which sets
exts->actions to NULL and returns 1 to caller fl_change().

fl_change() treats err == 1 as success, calling tcf_exts_validate_ex()
which calls tcf_action_init() with exts->actions as argument, where it
is dereferenced.

Example trace:

BUG: kernel NULL pointer dereference, address: 0000000000000000
CPU: 114 PID: 16151 Comm: handler114 Kdump: loaded Not tainted 5.14.0-503.16.1.el9_5.x86_64 #1
RIP: 0010:tcf_action_init+0x1f8/0x2c0
Call Trace:
 tcf_action_init+0x1f8/0x2c0
 tcf_exts_validate_ex+0x175/0x190
 fl_change+0x537/0x1120 [cls_flower]

## References
- https://git.kernel.org/stable/c/071ed42cff4fcdd89025d966d48eabef59913bf2
- https://git.kernel.org/stable/c/3c74b5787caf59bb1e9c5fe0a360643a71eb1e8a
- https://git.kernel.org/stable/c/3e4c56cf41876ef2a82f0877fe2a67648f8632b8
- https://git.kernel.org/stable/c/de4b679aa3b4da7ec34f639df068b914f20e3c3c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21857.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21857
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
