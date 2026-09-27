# [H] drm/vkms: Fix use after free and double free on init error

## Summary
Severity: High
Advisory: CVE-2025-22097
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22097
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vkms: Fix use after free and double free on init error

If the driver initialization fails, the vkms_exit() function might
access an uninitialized or freed default_config pointer and it might
double free it.

Fix both possible errors by initializing default_config only when the
driver initialization succeeded.

## References
- https://git.kernel.org/stable/c/1f68f1cf09d06061eb549726ff8339e064eddebd
- https://git.kernel.org/stable/c/49a69f67f53518bdd9b7eeebf019a2da6cc0e954
- https://git.kernel.org/stable/c/561fc0c5cf41f646f3e9e61784cbc0fc832fb936
- https://git.kernel.org/stable/c/79d138d137b80eeb0a83244d1cff29e64cf91067
- https://git.kernel.org/stable/c/b8a18bb53e06d6d3c1fd03d12533d6e333ba8853
- https://git.kernel.org/stable/c/d5eb8e347905ab17788a7903fa1d3d06747355f5
- https://git.kernel.org/stable/c/ed15511a773df86205bda66c37193569575ae828
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22097.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22097
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
