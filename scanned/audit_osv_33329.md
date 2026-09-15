# [H] iio: light: Add check for array bounds in veml6075_read_int_time_ms

## Summary
Severity: High
Advisory: CVE-2025-40114
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-40114
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: light: Add check for array bounds in veml6075_read_int_time_ms

The array contains only 5 elements, but the index calculated by
veml6075_read_int_time_index can range from 0 to 7,
which could lead to out-of-bounds access. The check prevents this issue.

Coverity Issue
CID 1574309: (#1 of 1): Out-of-bounds read (OVERRUN)
overrun-local: Overrunning array veml6075_it_ms of 5 4-byte
elements at element index 7 (byte offset 31) using
index int_index (which evaluates to 7)

This is hardening against potentially broken hardware. Good to have
but not necessary to backport.

## References
- https://git.kernel.org/stable/c/18a08b5632809faa671279b3cd27d5f96cc5a3f0
- https://git.kernel.org/stable/c/7a40b52d4442178bee0cf1c36bc450ab951cef0f
- https://git.kernel.org/stable/c/9c40a68b7f97fa487e6c7e67fcf4f846a1f96692
- https://git.kernel.org/stable/c/ee735aa33db16c1fb5ebccbaf84ad38f5583f3cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40114.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40114
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
