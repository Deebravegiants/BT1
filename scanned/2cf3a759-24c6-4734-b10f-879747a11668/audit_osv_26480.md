# [M] drm/amd/display: Fix possible underflow for displays with large vblank

## Summary
Severity: Medium
Advisory: CVE-2023-53258
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53258
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.43, >=6.2.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix possible underflow for displays with large vblank

[Why]
Underflow observed when using a display with a large vblank region
and low refresh rate

[How]
Simplify calculation of vblank_nom

Increase value for VBlankNomDefaultUS to 800us

## References
- https://git.kernel.org/stable/c/1a4bcdbea4319efeb26cc4b05be859a7867e02dc
- https://git.kernel.org/stable/c/64bc8e10c87adf60b2d32aacf3afb288e51d5a62
- https://git.kernel.org/stable/c/d5741133e6e2f304b40ca1da0e16f62af06f4d22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53258.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53258
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
