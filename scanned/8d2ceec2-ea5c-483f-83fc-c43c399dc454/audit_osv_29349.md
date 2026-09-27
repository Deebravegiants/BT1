# [H] net: mana: Fix possible double free in error handling path

## Summary
Severity: High
Advisory: CVE-2024-42069
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42069
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.37, >=6.7.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: Fix possible double free in error handling path

When auxiliary_device_add() returns error and then calls
auxiliary_device_uninit(), callback function adev_release
calls kfree(madev). We shouldn't call kfree(madev) again
in the error handling path. Set 'madev' to NULL.

## References
- https://git.kernel.org/stable/c/1864b8224195d0e43ddb92a8151f54f6562090cc
- https://git.kernel.org/stable/c/3243e64eb4d897c3eeb48b2a7221ab5a95e1282a
- https://git.kernel.org/stable/c/ed45c0a0b662079d4c0e518014cc148c753979b4
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42069.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42069
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
