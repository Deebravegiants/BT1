# [M] drm/radeon: fix uninitialized size issue in radeon_vce_cs_parse()

## Summary
Severity: Medium
Advisory: CVE-2025-21996
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-21996
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/radeon: fix uninitialized size issue in radeon_vce_cs_parse()

On the off chance that command stream passed from userspace via
ioctl() call to radeon_vce_cs_parse() is weirdly crafted and
first command to execute is to encode (case 0x03000001), the function
in question will attempt to call radeon_vce_cs_reloc() with size
argument that has not been properly initialized. Specifically, 'size'
will point to 'tmp' variable before the latter had a chance to be
assigned any value.

Play it safe and init 'tmp' with 0, thus ensuring that
radeon_vce_cs_reloc() will catch an early error in cases like these.

Found by Linux Verification Center (linuxtesting.org) with static
analysis tool SVACE.

(cherry picked from commit 2d52de55f9ee7aaee0e09ac443f77855989c6b68)

## References
- https://git.kernel.org/stable/c/0effb378ebce52b897f85cd7f828854b8c7cb636
- https://git.kernel.org/stable/c/3ce08215cad55c10a6eeeb33d3583b6cfffe3ab8
- https://git.kernel.org/stable/c/5b4d9d20fd455a97920cf158dd19163b879cf65d
- https://git.kernel.org/stable/c/78b07dada3f02f77762d0755a96d35f53b02be69
- https://git.kernel.org/stable/c/9b2da9c673a0da1359a2151f7ce773e2f77d71a9
- https://git.kernel.org/stable/c/dd1801aa01bba1760357f2a641346ae149686713
- https://git.kernel.org/stable/c/dd8689b52a24807c2d5ce0a17cb26dc87f75235c
- https://git.kernel.org/stable/c/f5e049028124f755283f2c07e7a3708361ed1dc8
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21996.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21996
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
