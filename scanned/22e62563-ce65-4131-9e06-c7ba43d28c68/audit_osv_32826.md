# [H] gpio: virtuser: fix potential out-of-bound write

## Summary
Severity: High
Advisory: CVE-2025-38082
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38082
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.32, >=6.13.0 <6.14.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: virtuser: fix potential out-of-bound write

If the caller wrote more characters, count is truncated to the max
available space in "simple_write_to_buffer". Check that the input
size does not exceed the buffer size. Write a zero termination
afterwards.

## References
- https://git.kernel.org/stable/c/7118be7c6072f40391923543fdd1563b8d56377c
- https://git.kernel.org/stable/c/afe090366f470f77e140ff3407db813f57852c04
- https://git.kernel.org/stable/c/b96feaaa0fda1e3871b438143c3446954b32d3a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38082.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38082
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
