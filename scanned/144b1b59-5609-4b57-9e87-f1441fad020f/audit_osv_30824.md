# [H] net: ieee802154: do not leave a dangling sk pointer in ieee802154_create()

## Summary
Severity: High
Advisory: CVE-2024-56602
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56602
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ieee802154: do not leave a dangling sk pointer in ieee802154_create()

sock_init_data() attaches the allocated sk object to the provided sock
object. If ieee802154_create() fails later, the allocated sk object is
freed, but the dangling pointer remains in the provided sock object, which
may allow use-after-free.

Clear the sk pointer in the sock object on error.

## References
- https://git.kernel.org/stable/c/03caa9bfb9fde97fb53d33decd7364514e6825cb
- https://git.kernel.org/stable/c/14959fd7538b3be6d7617d9e60e404d6a8d4fd1f
- https://git.kernel.org/stable/c/1d5fe782c0ff068d80933f9cfd0fd39d5434bbc9
- https://git.kernel.org/stable/c/2b46994a6e76c8cc5556772932b9b60d03a55cd8
- https://git.kernel.org/stable/c/b4982fbf13042e3bb33e04eddfea8b1506b5ea65
- https://git.kernel.org/stable/c/b4fcd63f6ef79c73cafae8cf4a114def5fc3d80d
- https://git.kernel.org/stable/c/e8bd6c5f5dc2234b4ea714380aedeea12a781754
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56602.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56602
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
