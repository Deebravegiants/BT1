# [H] hfs/hfsplus: fix u32 overflow in check_and_correct_requested_length

## Summary
Severity: High
Advisory: CVE-2026-64361
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64361
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.17.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfs/hfsplus: fix u32 overflow in check_and_correct_requested_length

check_and_correct_requested_length() compares (off + len) against
node_size using u32 arithmetic.  When the caller passes a large len
value (e.g. from an underflowed subtraction in hfs_brec_remove()),
off + len can wrap past 2^32 and produce a small result, causing the
bounds check to pass when it should fail.

For example, with off=14 and len=0xFFFFFFF2 (underflowed from
data_off - keyoffset - size in hfs_brec_remove), off + len wraps to 6,
which is less than a typical node_size of 512, so the check passes and
the subsequent memmove reads ~4GB past the node buffer.

Fix this by widening the addition to u64 before comparing against
node_size.  This prevents the u32 wrap while keeping the logic
straightforward.

## References
- https://git.kernel.org/stable/c/607217f7ad419b53926f71e3f75001813bbc08ad
- https://git.kernel.org/stable/c/671c3fcc2ad31c1311ea6414382a2d95104ae1b9
- https://git.kernel.org/stable/c/7399c3baee7bb622a92f0b895cd4d3009a693f2b
- https://git.kernel.org/stable/c/966cb76fb2857a4242cab6ea2ea17acf818a3da7
- https://git.kernel.org/stable/c/b6a481642ea1977be2f84dc08c5affd742c177e7
- https://git.kernel.org/stable/c/c25d3c931a63e762fcaa9cb125b901c53b62403f
- https://git.kernel.org/stable/c/c8dd112173c02adf539fe2ad34a45f5e0068780d
- https://git.kernel.org/stable/c/fc9d1447ca3cdc78d2e4ace1ce1f3a7c77ca08b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64361.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64361
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
