# [H] HID: wacom: fix slab-out-of-bounds write in wacom_wac_queue_insert

## Summary
Severity: High
Advisory: CVE-2026-64366
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64366
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: wacom: fix slab-out-of-bounds write in wacom_wac_queue_insert

wacom_wac_queue_insert() calls kfifo_skip() in a loop when the kfifo
doesn't have enough space for the incoming report. If the kfifo is
empty, kfifo_skip() reads stale data left in the kmalloc'd buffer
via __kfifo_peek_n() and interprets it as a record length, advancing
fifo->out by that garbage value. This corrupts the internal kfifo
state, causing kfifo_unused() to return a value much larger than the
actual buffer size, which bypasses __kfifo_in_r()'s guard:

  if (len + recsize > kfifo_unused(fifo))
      return 0;

kfifo_copy_in() then performs an out-of-bounds memcpy, writing up to
3842 bytes past the 256-byte buffer.

Add a !kfifo_is_empty() condition to the while loop so kfifo_skip()
is never called on an empty fifo, and check the return value of
kfifo_in() to reject reports that are too large for the fifo.

## References
- https://git.kernel.org/stable/c/57bdd10ad50d68341f500a7b330f0d8949e510ec
- https://git.kernel.org/stable/c/6b3014ec0e9a390ca563030b2d7689921f0daef5
- https://git.kernel.org/stable/c/ca899a926c11a59211b764b0155d9a1cdcc32b81
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64366.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64366
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
