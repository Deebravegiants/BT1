# [H] s390/dasd: Fix undersized format-check buffer

## Summary
Severity: High
Advisory: CVE-2026-80710
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80710
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/dasd: Fix undersized format-check buffer

fmt_buffer_size in dasd_eckd_check_device_format() is declared as
int, even though one of the multiplicands, sizeof(struct eckd_count),
is a size_t. The expression

    trkcount * rpt_max * sizeof(struct eckd_count)

is therefore correctly evaluated at 64-bit width, but the result is
silently truncated when it is stored back into the 32-bit
fmt_buffer_size variable. For a sufficiently large track range
(start_unit/stop_unit are caller-controlled) this truncation
yields a buffer size far smaller than the number of tracks actually
requested. kzalloc() then succeeds with an undersized allocation,
while the subsequent channel program build still operates on the
untruncated track count and writes past the end of that buffer.

Compute the buffer size with check_mul_overflow() and keep it in a
size_t, so that a value that no longer fits results in -EINVAL
instead of a silently truncated allocation size.

## References
- https://git.kernel.org/stable/c/7f40b346462f563a0d6e841a77b5163d2a882a04
- https://git.kernel.org/stable/c/87f3389cd3920714c53e704778f7ca7f1cf0c39c
- https://git.kernel.org/stable/c/9f88dda2f22927d22498801a92cab6a9424eaf86
- https://git.kernel.org/stable/c/aca18289c86f22d3fc2f3f6ff615286e7b1702f6
- https://git.kernel.org/stable/c/e16e0fc54120cee3c6f0362de95aab6792865857
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80710.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80710
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
