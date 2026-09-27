# [M] drm: bridge: it66121: Fix invalid connector dereference

## Summary
Severity: Medium
Advisory: CVE-2023-52861
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52861
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: bridge: it66121: Fix invalid connector dereference

Fix the NULL pointer dereference when no monitor is connected, and the
sound card is opened from userspace.

Instead return an empty buffer (of zeroes) as the EDID information to
the sound framework if there is no connector attached.

## References
- https://git.kernel.org/stable/c/1374561a7cbc9a000b77bb0473bb2c19daf18d86
- https://git.kernel.org/stable/c/1669d7b21a664aa531856ce85b01359a376baebc
- https://git.kernel.org/stable/c/2c80c4f0d2845645f41cbb7c9304c8efbdbd4331
- https://git.kernel.org/stable/c/d0375f6858c4ff7244b62b02eb5e93428e1916cd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52861.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52861
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
