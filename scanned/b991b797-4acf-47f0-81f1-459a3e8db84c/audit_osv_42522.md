# [H] usb: gadget: dummy_hcd: prevent fifo_req reuse during giveback

## Summary
Severity: High
Advisory: CVE-2026-68370
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68370
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: dummy_hcd: prevent fifo_req reuse during giveback

dummy_hcd embeds a single shared usb_request (dum->fifo_req) that the
"emulated single-request FIFO" fast-path in dummy_queue() reuses for
small IN transfers: it copies the caller's request into it
(req->req = *_req) and queues it, treating list_empty(&fifo_req.queue)
as "the slot is free".

The completion side (dummy_timer/transfer/nuke/dummy_dequeue) follows
the standard pattern: list_del_init(&req->queue) unlinks the request,
then the lock is dropped and usb_gadget_giveback_request() invokes
req->complete().  But list_del_init() makes fifo_req.queue look empty
*before* the completion callback returns, so a concurrent dummy_queue()
on another CPU sees the slot as free, reuses fifo_req and runs
req->req = *_req -- overwriting req->complete while dummy_timer is
mid-calling it.  The indirect call then jumps to a clobbered pointer,
causing a general protection fault / page fault in dummy_timer
(syzkaller extid faf3a6cf579fc65591ca).  The clobbering write is an
in-bounds memcpy on a live shared object, so KASAN cannot flag it.

Add a fifo_req_busy bit covering the shared request's whole lifetime:
set it in dummy_queue() when the FIFO fast-path takes fifo_req (making
it the fast-path guard, replacing the list_empty(&fifo_req.queue)
test), and clear it after the completion callback has returned, via a
dummy_giveback() helper used at all four gadget-request giveback
sites.  The shared slot can no longer be reused until its completion
callback has finished.

## References
- https://git.kernel.org/stable/c/16a685172abc9233728830e27d26ffa778975b51
- https://git.kernel.org/stable/c/3cab0e5498d0fbb21fe1a9181f7bda9a844a697e
- https://git.kernel.org/stable/c/67b589d09a96882d56842dced5698ed8dd06ce45
- https://git.kernel.org/stable/c/95f30a21612cc65761c58ba044b1767699437317
- https://git.kernel.org/stable/c/d5e5cd3654d2b5359a12ea6586120f05b28634ee
- https://git.kernel.org/stable/c/e239ea91b48180ed48a86ac25643832a02c88456
- https://git.kernel.org/stable/c/e24b33618231034bf01dfaff4fd3409d4b4d5b2e
- https://git.kernel.org/stable/c/e2b2740f1242bc70b5b46da2cdbbaa419f490e59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68370.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68370
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
