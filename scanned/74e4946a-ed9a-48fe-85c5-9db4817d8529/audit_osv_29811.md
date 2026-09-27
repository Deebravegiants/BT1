# [H] drm/amd/display: Skip inactive planes within ModeSupportAndSystemConfiguration

## Summary
Severity: High
Advisory: CVE-2024-46812
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46812
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.109, >=6.2.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Skip inactive planes within ModeSupportAndSystemConfiguration

[Why]
Coverity reports Memory - illegal accesses.

[How]
Skip inactive planes.

## References
- https://git.kernel.org/stable/c/2fd32a65f2e78eff0862c8fdf7815ca6bb44fb2e
- https://git.kernel.org/stable/c/3300a039caf850376bc3416c808cd8879da412bb
- https://git.kernel.org/stable/c/4331ae2788e779b11f3aad40c04be6c64831f2a2
- https://git.kernel.org/stable/c/8406158a546441b73f0b216aedacbf9a1e5748fb
- https://git.kernel.org/stable/c/a54f7e866cc73a4cb71b8b24bb568ba35c8969df
- https://git.kernel.org/stable/c/ee9d6df6d9172917d9ddbd948bb882652d5ecd29
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46812.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46812
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
