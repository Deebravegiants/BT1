# [H] net/sched: cls_u32: validate offshift to prevent shift-out-of-bounds

## Summary
Severity: High
Advisory: CVE-2026-74544
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74544
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: cls_u32: validate offshift to prevent shift-out-of-bounds

u32_change() copies the user-provided tc_u32_sel.offshift (unsigned char,
0-255) into the kernel knode object without bounds validation. When a
packet later hits u32_classify() with TC_U32_VAROFFSET set, it evaluates
`ntohs(offmask & *data) >> offshift` where the left operand is a 16-bit
value promoted to a 32-bit int. Any offshift >= 32 is undefined behavior
per C11 6.5.7p3, triggerable by an unprivileged user via user/network
namespaces.

UBSAN: shift-out-of-bounds in net/sched/cls_u32.c:236:43
shift exponent 32 is too large for 32-bit type int

Fix this by rejecting offshift >= 16 during filter creation in
u32_change().

## References
- https://git.kernel.org/stable/c/313cb9ffc4101a885d791facf4b5ea3d5e06144d
- https://git.kernel.org/stable/c/aef96eead2860cbfa371e4471d4f04412213b958
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74544.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74544
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
