# [H] fuse: clear intr_entry in fuse_resend and fuse_remove_pending_req

## Summary
Severity: High
Advisory: CVE-2026-64265
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64265
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse: clear intr_entry in fuse_resend and fuse_remove_pending_req

When fuse_resend() moves a request from fpq->processing back to
fiq->pending, it sets FR_PENDING and clears FR_SENT but does not
remove the requests intr_entry from fiq->interrupts.  If the
request had FR_INTERRUPTED set from a prior signal, intr_entry
remains dangling on fiq->interrupts.  When the requesting task
then receives a fatal signal, fuse_remove_pending_req() sees
FR_PENDING=1, removes the request from fiq->pending and frees it
via the refcount path, also without cleaning intr_entry.  The
stale intr_entry causes use-after-free when fuse_read_interrupt()
iterates fiq->interrupts:
  - list_del_init(&req->intr_entry) -> UAF write on freed slab
  - req->in.h.unique -> UAF read, data leaked to userspace

Remove intr_entry from fiq->interrupts in fuse_resend() for
interrupted requests before they are placed back on fiq->pending.

Add a WARN_ON if the intr_entry is not empty on request destruction.

## References
- https://git.kernel.org/stable/c/1d8ecd0cd696a5df0b2f72046a4ccee5d2a8ec2c
- https://git.kernel.org/stable/c/7366e6f4d2b4c7002b13fb01219e83679dad4127
- https://git.kernel.org/stable/c/893479015cb6442fd389d3b553ab3036c9541715
- https://git.kernel.org/stable/c/f8fce75fedf73ac72aa09163deb8f4291fdcaad2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64265.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64265
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
