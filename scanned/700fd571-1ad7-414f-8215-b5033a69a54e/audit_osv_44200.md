# [H] fbdev: bound mode sysfs output to the sysfs buffer

## Summary
Severity: High
Advisory: CVE-2026-80580
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80580
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: bound mode sysfs output to the sysfs buffer

mode_string() uses snprintf() which can return a value larger than the
remaining buffer space. show_modes() accumulates the return value into i
without checking whether i has reached PAGE_SIZE, causing the offset to
advance past the sysfs buffer if the modelist is long enough.

Add a size parameter to mode_string() and use scnprintf() to return
only the bytes actually written. Add an early return when offset
already exceeds the buffer. In show_modes(), stop accumulating once
the buffer is full.

## References
- https://git.kernel.org/stable/c/873a1aa15c313263f2e18b38cf525623cc4fabf6
- https://git.kernel.org/stable/c/d15d51fb26e830af58f3f21964f1c09c239077ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80580.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80580
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
