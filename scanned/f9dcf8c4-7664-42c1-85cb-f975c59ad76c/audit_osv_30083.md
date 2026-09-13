# [H] drm/stm: Avoid use-after-free issues with crtc and plane

## Summary
Severity: High
Advisory: CVE-2024-49992
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49992
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/stm: Avoid use-after-free issues with crtc and plane

ltdc_load() calls functions drm_crtc_init_with_planes(),
drm_universal_plane_init() and drm_encoder_init(). These functions
should not be called with parameters allocated with devm_kzalloc()
to avoid use-after-free issues [1].

Use allocations managed by the DRM framework.

Found by Linux Verification Center (linuxtesting.org).

[1]
https://lore.kernel.org/lkml/u366i76e3qhh3ra5oxrtngjtm2u5lterkekcz6y2jkndhuxzli@diujon4h7qwb/

## References
- https://git.kernel.org/stable/c/0a1741d10da29aa84955ef89ae9a03c4b6038657
- https://git.kernel.org/stable/c/19dd9780b7ac673be95bf6fd6892a184c9db611f
- https://git.kernel.org/stable/c/454e5d7e671946698af0f201e48469e5ddb42851
- https://git.kernel.org/stable/c/b22eec4b57d04befa90e8554ede34e6c67257606
- https://git.kernel.org/stable/c/d02611ff001454358be6910cb926799e2d818716
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49992.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49992
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
