# [H] fbdev: efifb: Register sysfs groups through driver core

## Summary
Severity: High
Advisory: CVE-2024-49925
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49925
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.15.209, >=5.16.0 <6.1.120, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: efifb: Register sysfs groups through driver core

The driver core can register and cleanup sysfs groups already.
Make use of that functionality to simplify the error handling and
cleanup.

Also avoid a UAF race during unregistering where the sysctl attributes
were usable after the info struct was freed.

## References
- https://git.kernel.org/stable/c/2a9c40c72097b583b23aeb2a26d429ccfc81fbc1
- https://git.kernel.org/stable/c/2d97b85eb5a86766ad0f8ea3d121e6ae144e3ed8
- https://git.kernel.org/stable/c/36bfefb6baaa8e46de44f4fd919ce4347337620f
- https://git.kernel.org/stable/c/4684d69b9670a83992189f6271dc0fcdec4ed0d7
- https://git.kernel.org/stable/c/872cd2d029d2c970a8a1eea88b48dab2b3f2e93a
- https://git.kernel.org/stable/c/95cdd538e0e5677efbdf8aade04ec098ab98f457
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49925.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
