# [H] ring-buffer: Prevent subbuf order change when resizing is disabled

## Summary
Severity: High
Advisory: CVE-2026-74634
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74634
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ring-buffer: Prevent subbuf order change when resizing is disabled

Because ring_buffer_subbuf_order_set() frees buffer pages, we can't
allow it when resizing is disabled. A non-consuming reader is at risk of
use-after-free (rb_advance_iter()).

Return -EBUSY on resize_disabled, matching ring_buffer_resize()
behaviour.

## References
- https://git.kernel.org/stable/c/62978cf6347972c04130e4e841ba404504d92b32
- https://git.kernel.org/stable/c/7568e9e717e7540bd05bcc007f5d76fcaff3cdff
- https://git.kernel.org/stable/c/b45b91db41379ee5fb36c187d6d7c37b725cbe8e
- https://git.kernel.org/stable/c/bf98d7b0d5a99991e47e66cee4eb1d3fa514be97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74634.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74634
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
