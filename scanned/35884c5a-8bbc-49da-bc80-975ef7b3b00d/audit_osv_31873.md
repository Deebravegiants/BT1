# [M] usb: typec: ucsi: Fix NULL pointer access

## Summary
Severity: Medium
Advisory: CVE-2025-21918
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21918
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.133, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: typec: ucsi: Fix NULL pointer access

Resources should be released only after all threads that utilize them
have been destroyed.
This commit ensures that resources are not released prematurely by waiting
for the associated workqueue to complete before deallocating them.

## References
- https://git.kernel.org/stable/c/079a3e52f3e751bb8f5937195bdf25c5d14fdff0
- https://git.kernel.org/stable/c/46fba7be161bb89068958138ea64ec33c0b446d4
- https://git.kernel.org/stable/c/592a0327d026a122e97e8e8bb7c60cbbe7697344
- https://git.kernel.org/stable/c/7a735a8a46f6ebf898bbefd96659ca5da798bce0
- https://git.kernel.org/stable/c/b13abcb7ddd8d38de769486db5bd917537b32ab1
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21918.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21918
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
