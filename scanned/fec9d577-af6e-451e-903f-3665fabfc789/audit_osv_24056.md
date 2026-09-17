# [H] IB/hfi1: Correctly move list in sc_disable()

## Summary
Severity: High
Advisory: CVE-2022-49931
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49931
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.15.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/hfi1: Correctly move list in sc_disable()

Commit 13bac861952a ("IB/hfi1: Fix abba locking issue with sc_disable()")
incorrectly tries to move a list from one list head to another.  The
result is a kernel crash.

The crash is triggered when a link goes down and there are waiters for a
send to complete.  The following signature is seen:

  BUG: kernel NULL pointer dereference, address: 0000000000000030
  [...]
  Call Trace:
   sc_disable+0x1ba/0x240 [hfi1]
   pio_freeze+0x3d/0x60 [hfi1]
   handle_freeze+0x27/0x1b0 [hfi1]
   process_one_work+0x1b0/0x380
   ? process_one_work+0x380/0x380
   worker_thread+0x30/0x360
   ? process_one_work+0x380/0x380
   kthread+0xd7/0x100
   ? kthread_complete_and_exit+0x20/0x20
   ret_from_fork+0x1f/0x30

The fix is to use the correct call to move the list.

## References
- https://git.kernel.org/stable/c/1afac08b39d85437187bb2a92d89a741b1078f55
- https://git.kernel.org/stable/c/25760a41e3802f54aadcc31385543665ab349b8e
- https://git.kernel.org/stable/c/7c4260f8f188df32414a5ecad63e8b934c2aa3f0
- https://git.kernel.org/stable/c/b8bcff99b07cc175a6ee12a52db51cdd2229586c
- https://git.kernel.org/stable/c/ba95409d6b580501ff6d78efd00064f7df669926
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49931.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49931
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
