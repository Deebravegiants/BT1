# [H] drm/amdgpu: Fix out-of-bounds write warning

## Summary
Severity: High
Advisory: CVE-2024-46725
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46725
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.109, >=6.2.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix out-of-bounds write warning

Check the ring type value to fix the out-of-bounds
write warning

## References
- https://git.kernel.org/stable/c/130bee397b9cd52006145c87a456fd8719390cb5
- https://git.kernel.org/stable/c/919f9bf9997b8dcdc132485ea96121e7d15555f9
- https://git.kernel.org/stable/c/a60d1f7ff62e453dde2d3b4907e178954d199844
- https://git.kernel.org/stable/c/be1684930f5262a622d40ce7a6f1423530d87f89
- https://git.kernel.org/stable/c/c253b87c7c37ec40a2e0c84e4a6b636ba5cd66b2
- https://git.kernel.org/stable/c/cf2db220b38301b6486a0f11da24a0f317de558c
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46725.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46725
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
