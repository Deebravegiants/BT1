# [H] parport: Proper fix for array out-of-bounds access

## Summary
Severity: High
Advisory: CVE-2024-50074
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50074
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

parport: Proper fix for array out-of-bounds access

The recent fix for array out-of-bounds accesses replaced sprintf()
calls blindly with snprintf().  However, since snprintf() returns the
would-be-printed size, not the actually output size, the length
calculation can still go over the given limit.

Use scnprintf() instead of snprintf(), which returns the actually
output letters, for addressing the potential out-of-bounds access
properly.

## References
- https://git.kernel.org/stable/c/02ac3a9ef3a18b58d8f3ea2b6e46de657bf6c4f9
- https://git.kernel.org/stable/c/1826b6d69bbb7f9ae8711827facbb2ad7f8d0aaa
- https://git.kernel.org/stable/c/2a8b26a09c8e3ea03da1ef3cd0ef6b96e559fba6
- https://git.kernel.org/stable/c/440311903231c6e6c9bcf8acb6a2885a422e00bc
- https://git.kernel.org/stable/c/66029078fee00646e2e9dbb8f41ff7819f8e7569
- https://git.kernel.org/stable/c/8aadef73ba3b325704ed5cfc4696a25c350182cf
- https://git.kernel.org/stable/c/b0641e53e6cb937487b6cfb15772374f0ba149b3
- https://git.kernel.org/stable/c/fca048f222ce9dcbde5708ba2bf81d85a4a27952
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50074.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50074
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
