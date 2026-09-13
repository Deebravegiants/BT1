# [M] pstore/platform: Add check for kstrdup

## Summary
Severity: Medium
Advisory: CVE-2023-52869
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52869
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

pstore/platform: Add check for kstrdup

Add check for the return value of kstrdup() and return the error
if it fails in order to avoid NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/1c426da79f9fc7b761021b5eb44185ba119cd44a
- https://git.kernel.org/stable/c/379b120e4f27fd1cf636a5f85570c4d240a3f688
- https://git.kernel.org/stable/c/63f637309baadf81a095f2653e3b807d4b5814b9
- https://git.kernel.org/stable/c/a19d48f7c5d57c0f0405a7d4334d1d38fe9d3c1c
- https://git.kernel.org/stable/c/ad5cb6deb41417ef41b9d6ff54f789212108606f
- https://git.kernel.org/stable/c/bb166bdae1a7d7db30e9be7e6ccaba606debc05f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52869.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52869
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
