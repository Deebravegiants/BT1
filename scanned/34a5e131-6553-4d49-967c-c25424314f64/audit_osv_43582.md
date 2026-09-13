# [H] accel/amdxdna: Adjust size for copy_to_user()

## Summary
Severity: High
Advisory: CVE-2026-74419
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74419
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Adjust size for copy_to_user()

The amount of data returned to user space should be limited by the buffer
size provided by the application. If the buffer is smaller than the data
size, return only the portion that fits instead of failing.

## References
- https://git.kernel.org/stable/c/097e57195ef813735c8b714d6503bf3ad0742515
- https://git.kernel.org/stable/c/6e87001fe19f251e2ae14373bc76554358a13df2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74419.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74419
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
