# [H] net: inet: do not leave a dangling sk pointer in inet_create()

## Summary
Severity: High
Advisory: CVE-2024-56601
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56601
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: inet: do not leave a dangling sk pointer in inet_create()

sock_init_data() attaches the allocated sk object to the provided sock
object. If inet_create() fails later, the sk object is freed, but the
sock object retains the dangling pointer, which may create use-after-free
later.

Clear the sk pointer in the sock object on error.

## References
- https://git.kernel.org/stable/c/25447c6aaa7235f155292b0c58a067347e8ae891
- https://git.kernel.org/stable/c/2bc34d8c8898ae9fddf4612501aabb22d76c2b2c
- https://git.kernel.org/stable/c/3e8258070b0f2aba66b3ef18883de229674fb288
- https://git.kernel.org/stable/c/691d6d816f93b2a1008c14178399061466e674ef
- https://git.kernel.org/stable/c/9365fa510c6f82e3aa550a09d0c5c6b44dbc78ff
- https://git.kernel.org/stable/c/b4513cfd3a10c03c660d5d3d26c2e322efbfdd9b
- https://git.kernel.org/stable/c/f8a3f255f7509a209292871715cda03779640c8d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56601.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56601
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
