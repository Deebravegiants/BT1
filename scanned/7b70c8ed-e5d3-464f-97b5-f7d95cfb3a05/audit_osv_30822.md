# [H] net: inet6: do not leave a dangling sk pointer in inet6_create()

## Summary
Severity: High
Advisory: CVE-2024-56600
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56600
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: inet6: do not leave a dangling sk pointer in inet6_create()

sock_init_data() attaches the allocated sk pointer to the provided sock
object. If inet6_create() fails later, the sk object is released, but the
sock object retains the dangling sk pointer, which may cause use-after-free
later.

Clear the sock sk pointer on error.

## References
- https://git.kernel.org/stable/c/276a473c956fb55a6f3affa9ff232e10fffa7b43
- https://git.kernel.org/stable/c/35360255ca30776dee34d9fa764cffa24d0a5f65
- https://git.kernel.org/stable/c/706b07b7b37f886423846cb38919132090bc40da
- https://git.kernel.org/stable/c/79e16a0d339532ea832d85798eb036fc4f9e0cea
- https://git.kernel.org/stable/c/9df99c395d0f55fb444ef39f4d6f194ca437d884
- https://git.kernel.org/stable/c/f2709d1271cfdf55c670ab5c5982139ab627ddc7
- https://git.kernel.org/stable/c/f44fceb71d72d29fb00e0ac84cdf9c081b03cd06
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56600.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56600
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
