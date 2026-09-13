# [H] media: chips-media: wave5: Move src_buf Removal to finish_encode

## Summary
Severity: High
Advisory: CVE-2026-68228
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68228
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: chips-media: wave5: Move src_buf Removal to finish_encode

During encoder processing, there is a case where the IRQ response could
return the buffer back to userspace via v4l2_m2m_buf_done call. In this
time, userspace could queue up this same buffer before start_encode removes
the index from the ready queue. This would then lead to a case where the
buffer in the ready queue could be a self loop due to the
WRITE_ONCE(prev->next, new) call in __list_add.

When __list_del is finally called, the loop is already made so nothing
points back to ready queue list head and pointers are poisoned.

A buffer should not be marked as DONE before the buffer is removed from
m2m ready queue. Move removal entirely to finish_encode.

## References
- https://git.kernel.org/stable/c/1ee2b2b189ddc7b23c8eee1145de42b8bd19fb06
- https://git.kernel.org/stable/c/b20157147089a9c16a38c7810e2fe6f2df8e3277
- https://git.kernel.org/stable/c/d681227ce43bfd74b6eb69beecd9b0bec1fd8b48
- https://git.kernel.org/stable/c/f24ca8b53fe15db40957bdaa40c9aa68e1557bbe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68228.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68228
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
