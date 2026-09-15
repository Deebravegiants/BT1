# [M] drm/nouveau/gr/gf100: Fix missing unlock in gf100_gr_chan_new()

## Summary
Severity: Medium
Advisory: CVE-2024-56752
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56752
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/nouveau/gr/gf100: Fix missing unlock in gf100_gr_chan_new()

When the call to gf100_grctx_generate() fails, unlock gr->fecs.mutex
before returning the error.

Fixes smatch warning:

drivers/gpu/drm/nouveau/nvkm/engine/gr/gf100.c:480 gf100_gr_chan_new() warn: inconsistent returns '&gr->fecs.mutex'.

## References
- https://git.kernel.org/stable/c/22b4a623c0f230540f02f4358744cce62ae12dbf
- https://git.kernel.org/stable/c/237f2dbfa00576bb1aa8dc2dce403c64e53270e6
- https://git.kernel.org/stable/c/24b1df744ef444f9846f52de4985790a5fd1c0de
- https://git.kernel.org/stable/c/a2f599046c671d6b46d93aed95b37241ce4504cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56752.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56752
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
