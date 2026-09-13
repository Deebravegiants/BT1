# [H] iio: fix potential out-of-bound write

## Summary
Severity: High
Advisory: CVE-2025-38667
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38667
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: fix potential out-of-bound write

The buffer is set to 20 characters. If a caller write more characters,
count is truncated to the max available space in "simple_write_to_buffer".
To protect from OoB access, check that the input size fit into buffer and
add a zero terminator after copy to the end of the copied data.

## References
- https://git.kernel.org/stable/c/16285a0931869baa618b1f5d304e1e9d090470a8
- https://git.kernel.org/stable/c/81a635b6eccd6fc889f6d07ab9583b705f739ce1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38667.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38667
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
