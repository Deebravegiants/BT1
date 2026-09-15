# [H] drm/amdgpu: validate GEM_CREATE domain combinations

## Summary
Severity: High
Advisory: CVE-2026-80541
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80541
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: validate GEM_CREATE domain combinations

AMDGPU_GEM_CREATE checked domain bits against AMDGPU_GEM_DOMAIN_MASK,
but did not validate domain combinations. Userspace could combine
CPU|GTT|VRAM with DOORBELL, GDS, GWS, or OA, making
amdgpu_bo_placement_from_domain() exceed AMDGPU_BO_MAX_PLACEMENTS and
hit BUG_ON().

Allow combinations only within CPU/GTT/VRAM, and require non-CPU/GTT/
VRAM domains to be specified one at a time. Return -EINVAL for invalid
combinations in amdgpu_gem_create_ioctl().

v2: Rename helper from amdgpu_gem_domain_valid() to
    amdgpu_gem_are_domains_valid() (Christian)

(cherry picked from commit db39852d0c39843cb02048dfb47e4b8c703e9080)

## References
- https://git.kernel.org/stable/c/220aa2589d7321fb68d2e8597862711b5f22ae0b
- https://git.kernel.org/stable/c/493355096e397f9217b41c8574ed2784c7351443
- https://git.kernel.org/stable/c/584e3d47736fe2e7184ef3fc16b00b41485f96c6
- https://git.kernel.org/stable/c/5c73485af7ad9c3ae592db3481f370bc07705391
- https://git.kernel.org/stable/c/5e9d136ad74df4edec67e502ce267597064d8f86
- https://git.kernel.org/stable/c/66133fc05c3af002f45de8a71b833c026ccbfba6
- https://git.kernel.org/stable/c/80f0b53860d02577709d69a312a29ca674b9297c
- https://git.kernel.org/stable/c/ce5da474c3ddf7cccec5dce6aa4296297dd7caff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80541.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80541
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
