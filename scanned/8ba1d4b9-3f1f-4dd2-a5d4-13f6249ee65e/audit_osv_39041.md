# [H] io_uring: fix physical SQE bounds check for SQE_MIXED 128-byte ops

## Summary
Severity: High
Advisory: CVE-2026-43442
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43442
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: fix physical SQE bounds check for SQE_MIXED 128-byte ops

When IORING_SETUP_SQE_MIXED is used without IORING_SETUP_NO_SQARRAY,
the boundary check for 128-byte SQE operations in io_init_req()
validated the logical SQ head position rather than the physical SQE
index.

The existing check:

  !(ctx->cached_sq_head & (ctx->sq_entries - 1))

ensures the logical position isn't at the end of the ring, which is
correct for NO_SQARRAY rings where physical == logical. However, when
sq_array is present, an unprivileged user can remap any logical
position to an arbitrary physical index via sq_array. Setting
sq_array[N] = sq_entries - 1 places a 128-byte operation at the last
physical SQE slot, causing the 128-byte memcpy in
io_uring_cmd_sqe_copy() to read 64 bytes past the end of the SQE
array.

Replace the cached_sq_head alignment check with a direct validation
of the physical SQE index, which correctly handles both sq_array and
NO_SQARRAY cases.

## References
- https://git.kernel.org/stable/c/1f794f9bed3e5cf7250a3b4daf112a72ed1513e9
- https://git.kernel.org/stable/c/6f02c6b196036dbb6defb4647d8707d29b7fe95b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43442.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43442
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
