# [H] Input: byd - synchronize timer deletion before freeing private data

## Summary
Severity: High
Advisory: CVE-2026-80572
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80572
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: byd - synchronize timer deletion before freeing private data

byd_disconnect() uses timer_delete() before freeing the driver's private
data.  This does not wait for a running byd_clear_touch() callback, which
dereferences the private data and its psmouse pointer.  A callback racing
with disconnect can therefore access the private data after it has been
freed.  The timer can also still be re-armed by byd_process_byte() while
the disconnect is in progress.

Use timer_shutdown_sync() before freeing the private data: it waits for
a running callback and turns any later re-arm attempt into a no-op.

## References
- https://git.kernel.org/stable/c/28d984a66b9e14be74986167b6ad40b5e0daf19a
- https://git.kernel.org/stable/c/2e509ef60ee41a2da0deb062c262bb530143fb37
- https://git.kernel.org/stable/c/84b205297fa15f97510342221d8c9a0119711478
- https://git.kernel.org/stable/c/8dbfd8e32a13e116790780ed0be82b5a05eb9916
- https://git.kernel.org/stable/c/c83e79c0842ed29860648bcce5022ef0ba5001c6
- https://git.kernel.org/stable/c/ee944a706a18322b4a2599eebe8040a2994e928f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80572.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80572
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
