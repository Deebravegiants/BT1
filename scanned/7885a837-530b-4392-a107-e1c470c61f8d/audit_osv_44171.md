# [H] drm/amdgpu: Fix UVD decode image min size calculation

## Summary
Severity: High
Advisory: CVE-2026-80540
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80540
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix UVD decode image min size calculation

This needs to use pitch instead of width. Also reject pitch
over 4096 to avoid overflow.

(cherry picked from commit b41c8cb12e202b220353332ab87dc01a11f69304)

## References
- https://git.kernel.org/stable/c/25ee120f3803ad9e416ef9f76f4c3234cc4d645b
- https://git.kernel.org/stable/c/271a7da84a6262a09de549912dcf6a749d169cb6
- https://git.kernel.org/stable/c/5cbd8af02b0b9c8723fa30edcf6fccab5170af8d
- https://git.kernel.org/stable/c/60539d517e8439621532d8c01091ac049c596b4b
- https://git.kernel.org/stable/c/b7549e3f96c78921751c4b3e69af729662130d83
- https://git.kernel.org/stable/c/b8bb9ba3f101a1b0011f785a577a4a0a38371174
- https://git.kernel.org/stable/c/bc7397a033ac52f6d8c9bb6510d61694b2a3fce7
- https://git.kernel.org/stable/c/d058f7a6709441afe1784eecd8c0643dd84750bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80540.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80540
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
