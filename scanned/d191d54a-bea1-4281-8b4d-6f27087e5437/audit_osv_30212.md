# [H] HID: amd_sfh: Switch to device-managed dmam_alloc_coherent()

## Summary
Severity: High
Advisory: CVE-2024-50189
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50189
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: amd_sfh: Switch to device-managed dmam_alloc_coherent()

Using the device-managed version allows to simplify clean-up in probe()
error path.

Additionally, this device-managed ensures proper cleanup, which helps to
resolve memory errors, page faults, btrfs going read-only, and btrfs
disk corruption.

## References
- https://git.kernel.org/stable/c/1c3b4c90479aa0375ec98fe1a802993ff96a5f47
- https://git.kernel.org/stable/c/4cd9c5a0fcadc39a05c978a01e15e0d1edc4be93
- https://git.kernel.org/stable/c/8c6ad37e5882073cab84901a31da9cb22f316276
- https://git.kernel.org/stable/c/9dfee956f53eea96d93ef1e13ab4ce020f4c58b3
- https://git.kernel.org/stable/c/c56f9ecb7fb6a3a90079c19eb4c8daf3bbf514b3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50189.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50189
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
