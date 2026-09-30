# [H] RDMA/umad: Reject negative data_len in ib_umad_write

## Summary
Severity: High
Advisory: CVE-2026-23243
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23243
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/umad: Reject negative data_len in ib_umad_write

ib_umad_write computes data_len from user-controlled count and the
MAD header sizes. With a mismatched user MAD header size and RMPP
header length, data_len can become negative and reach ib_create_send_mad().
This can make the padding calculation exceed the segment size and trigger
an out-of-bounds memset in alloc_send_rmpp_list().

Add an explicit check to reject negative data_len before creating the
send buffer.

KASAN splat:
[  211.363464] BUG: KASAN: slab-out-of-bounds in ib_create_send_mad+0xa01/0x11b0
[  211.364077] Write of size 220 at addr ffff88800c3fa1f8 by task spray_thread/102
[  211.365867] ib_create_send_mad+0xa01/0x11b0
[  211.365887] ib_umad_write+0x853/0x1c80

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1371ef6b1ecf3676b8942f5dfb3634fb0648128e
- https://git.kernel.org/stable/c/205955f29c26330b1dc7fdeadd5bb97c38e26f56
- https://git.kernel.org/stable/c/362e45fd9069ffa1523f9f1633b606ebf72060d7
- https://git.kernel.org/stable/c/52ab82cc5cf8ada5c3fb6ffe8f32fdb2fc27a34b
- https://git.kernel.org/stable/c/5551b02fdbfd85a325bb857f3a8f9c9f33397ed2
- https://git.kernel.org/stable/c/6eb2919474ca105c5b13d19574e25f0ddcf19ca2
- https://git.kernel.org/stable/c/9c80d688f402539dfc8f336de1380d6b4ee14316
- https://git.kernel.org/stable/c/a6a3e4af10993cb9e4b8f0548680aba0ab5f3b0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23243.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23243
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
