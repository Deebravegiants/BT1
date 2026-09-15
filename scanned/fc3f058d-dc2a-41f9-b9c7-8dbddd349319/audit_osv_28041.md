# [H] drm/amd/display: Fix a potential buffer overflow in 'dp_dsc_clock_en_read()'

## Summary
Severity: High
Advisory: CVE-2024-27045
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27045
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix a potential buffer overflow in 'dp_dsc_clock_en_read()'

Tell snprintf() to store at most 10 bytes in the output buffer
instead of 30.

Fixes the below:
drivers/gpu/drm/amd/amdgpu/../display/amdgpu_dm/amdgpu_dm_debugfs.c:1508 dp_dsc_clock_en_read() error: snprintf() is printing too much 30 vs 10

## References
- https://git.kernel.org/stable/c/440f059837418fac1695b65d3ebc6080d33be877
- https://git.kernel.org/stable/c/4b09715f1504f1b6e8dff0e9643630610bc05141
- https://git.kernel.org/stable/c/ad76fd30557d6a106c481e4606a981221ca525f7
- https://git.kernel.org/stable/c/cf114d8d4a8d78df272116a745bb43b48cef65f4
- https://git.kernel.org/stable/c/d346b3e5b25c95d504478507eb867cd3818775ab
- https://git.kernel.org/stable/c/eb9327af3621d26b1d83f767c97a3fe8191a3a65
- https://git.kernel.org/stable/c/ff28893c96c5e0927a4da10cd24a3522ca663515
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27045.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27045
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
