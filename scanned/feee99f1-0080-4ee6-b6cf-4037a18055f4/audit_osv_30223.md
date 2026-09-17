# [M] drm/radeon: Fix encoder->possible_clones

## Summary
Severity: Medium
Advisory: CVE-2024-50201
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50201
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/radeon: Fix encoder->possible_clones

Include the encoder itself in its possible_clones bitmask.
In the past nothing validated that drivers were populating
possible_clones correctly, but that changed in commit
74d2aacbe840 ("drm: Validate encoder->possible_clones").
Looks like radeon never got the memo and is still not
following the rules 100% correctly.

This results in some warnings during driver initialization:
Bogus possible_clones: [ENCODER:46:TV-46] possible_clones=0x4 (full encoder mask=0x7)
WARNING: CPU: 0 PID: 170 at drivers/gpu/drm/drm_mode_config.c:615 drm_mode_config_validate+0x113/0x39c
...

(cherry picked from commit 3b6e7d40649c0d75572039aff9d0911864c689db)

## References
- https://git.kernel.org/stable/c/1a235af0216411a32ab4db54f7bd19020b46c86d
- https://git.kernel.org/stable/c/28127dba64d8ae1a0b737b973d6d029908599611
- https://git.kernel.org/stable/c/68801730ebb9393460b30cd3885e407f15da27a9
- https://git.kernel.org/stable/c/c3cd27d85f0778f4ec07384d7516b33153759b8e
- https://git.kernel.org/stable/c/df75c78bfeff99f9b4815c3e79e2b1b1e34fe264
- https://git.kernel.org/stable/c/fda5dc80121b12871dc343ab37e0c3f0d138825d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50201.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
