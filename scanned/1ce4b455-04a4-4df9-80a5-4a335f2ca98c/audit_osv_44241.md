# [H] ufs: core: tracing: Do not dereference pointers in TP_printk()

## Summary
Severity: High
Advisory: CVE-2026-80661
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80661
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ufs: core: tracing: Do not dereference pointers in TP_printk()

The trace events in drivers/ufs/core/ufs_trace.h were converted to take a
pointer to the hba structure as an argument for the tracepoint and then in
TP_printk() the printing of the dev_name from the ring buffer was
converted to using the dev dereferenced pointer from the hba saved
pointer.

This is not allowed as the TP_printk() is executed at the time the trace
event is read from /sys/kernel/tracing/trace file. That can happen
literally, seconds, minutes, hours, weeks, days, or even months later!
There is no guarantee that the hba pointer will still exist by the time it
is dereferenced when the "trace" file is read.

Instead, save the device name from the hba pointer at the time the
tracepoint is called and place it into the ring buffer event. Then the
TP_printk() can read the name directly from the ring buffer and remove the
possibility that it will read a freed pointer and crash the kernel.

This was detected when testing the trace event code that looks for
TP_printk() parameters doing illegal derferences[1]

[1] https://lore.kernel.org/all/20260630184836.74d477b6@gandalf.local.home/

## References
- https://git.kernel.org/stable/c/2510434307a224078302019e52ab3c863fbe87fb
- https://git.kernel.org/stable/c/535fcf4b8a261fbb8cc4f91e4597343c135a90f2
- https://git.kernel.org/stable/c/e497fef9ad7e913f52de6f97e818f56915e96164
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80661.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80661
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
