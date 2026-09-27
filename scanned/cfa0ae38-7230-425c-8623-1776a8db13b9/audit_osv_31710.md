# [M] filemap: avoid truncating 64-bit offset to 32 bits

## Summary
Severity: Medium
Advisory: CVE-2025-21665
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21665
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

filemap: avoid truncating 64-bit offset to 32 bits

On 32-bit kernels, folio_seek_hole_data() was inadvertently truncating a
64-bit value to 32 bits, leading to a possible infinite loop when writing
to an xfs filesystem.

## References
- https://git.kernel.org/stable/c/09528bb1a4123e2a234eac2bc45a0e51e78dab43
- https://git.kernel.org/stable/c/280f1fb89afc01e7376f59ae611d54ca69e9f967
- https://git.kernel.org/stable/c/64e5fd96330df2ad278d1c4edcca581f26e5f76e
- https://git.kernel.org/stable/c/80fc836f3ebe2f2d2d2c80c698b7667974285a04
- https://git.kernel.org/stable/c/f505e6c91e7a22d10316665a86d79f84d9f0ba76
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21665.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21665
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
