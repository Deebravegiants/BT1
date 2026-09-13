# [H] io_uring/fdinfo: fix OOB read in SQE_MIXED wrap check

## Summary
Severity: High
Advisory: CVE-2026-31484
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31484
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/fdinfo: fix OOB read in SQE_MIXED wrap check

__io_uring_show_fdinfo() iterates over pending SQEs and, for 128-byte
SQEs on an IORING_SETUP_SQE_MIXED ring, needs to detect when the second
half of the SQE would be past the end of the sq_sqes array. The current
check tests (++sq_head & sq_mask) == 0, but sq_head is only incremented
when a 128-byte SQE is encountered, not on every iteration. The actual
array index is sq_idx = (i + sq_head) & sq_mask, which can be sq_mask
(the last slot) while the wrap check passes.

Fix by checking sq_idx directly. Keep the sq_head increment so the loop
still skips the second half of the 128-byte SQE on the next iteration.

## References
- https://git.kernel.org/stable/c/5170efd9c344c68a8075dcb8ed38d3f8a60e7ed4
- https://git.kernel.org/stable/c/ba21ab247a5be5382da7464b95afbe5f0e9aa503
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31484.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31484
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
