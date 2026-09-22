# [H] of: module: add buffer overflow check in of_modalias()

## Summary
Severity: High
Advisory: CVE-2024-38541
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38541
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.182, >=5.16.0 <6.1.136, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

of: module: add buffer overflow check in of_modalias()

In of_modalias(), if the buffer happens to be too small even for the 1st
snprintf() call, the len parameter will become negative and str parameter
(if not NULL initially) will point beyond the buffer's end. Add the buffer
overflow check after the 1st snprintf() call and fix such check after the
strlen() call (accounting for the terminating NUL char).

## References
- https://git.kernel.org/stable/c/0b0d5701a8bf02f8fee037e81aacf6746558bfd6
- https://git.kernel.org/stable/c/46795440ef2b4ac919d09310a69a404c5bc90a88
- https://git.kernel.org/stable/c/5d59fd637a8af42b211a92b2edb2474325b4d488
- https://git.kernel.org/stable/c/733e62786bdf1b2b9dbb09ba2246313306503414
- https://git.kernel.org/stable/c/c7f24b7d94549ff4623e8f41ea4d9f5319bd8ac8
- https://git.kernel.org/stable/c/cf7385cb26ac4f0ee6c7385960525ad534323252
- https://git.kernel.org/stable/c/e45b69360a63165377b30db4a1dfddd89ca18e9a
- https://git.kernel.org/stable/c/ee332023adfd5882808f2dabf037b32d6ce36f9e
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38541.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38541
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
