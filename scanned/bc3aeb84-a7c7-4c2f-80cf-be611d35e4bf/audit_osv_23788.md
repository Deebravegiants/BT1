# [M] drm/v3d: Fix null pointer dereference of pointer perfmon

## Summary
Severity: Medium
Advisory: CVE-2022-49485
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49485
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/v3d: Fix null pointer dereference of pointer perfmon

In the unlikely event that pointer perfmon is null the WARN_ON return path
occurs after the pointer has already been deferenced. Fix this by only
dereferencing perfmon after it has been null checked.

## References
- https://git.kernel.org/stable/c/1df8f8901babcc8c8eea2c067179e455b5c828fd
- https://git.kernel.org/stable/c/3b72deb784a7d4ae8519a5c584cd87c4b57aa6c8
- https://git.kernel.org/stable/c/4be045434923e549a50846a066a04b7b6c1d6d33
- https://git.kernel.org/stable/c/ce7a1ecf3f9f1fccaf67295307614511d8e11b13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49485.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49485
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
