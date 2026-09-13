# [H] drm/msm/snapshot: fix dumping of the unaligned regions

## Summary
Severity: High
Advisory: CVE-2026-64039
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64039
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/snapshot: fix dumping of the unaligned regions

The snapshotting code internally aligns data segment to 16 bytes. This
works fine for DPU code (where most of the regions are aligned), but
fails for snapshotting of the DSI data (because DSI data region is
shifted by 4 bytes). Fix the code by removing length alignment and by
accurately printing last registers in the region. While reworking the
code also fix the 16x memory overallocation in
msm_disp_state_dump_regs().

Patchwork: https://patchwork.freedesktop.org/patch/725449/

## References
- https://git.kernel.org/stable/c/070e40acc59ef7bedba0314f59971ba87fcc8ab0
- https://git.kernel.org/stable/c/0c90ececfad3fc5c4c43a75ece0e2d736ab3def1
- https://git.kernel.org/stable/c/1ef79be774706dddcfcace0331fa7ff32a73c73e
- https://git.kernel.org/stable/c/76824d2467feb1828b745d6add2541918d7be3da
- https://git.kernel.org/stable/c/8fb070cf95847b29ef6cb15ec2c0de2bf4704676
- https://git.kernel.org/stable/c/cdd1aaf0ee962f50810b9aef7928f2313989d55f
- https://git.kernel.org/stable/c/cecd34e046121d788a70b5c8b4f8a88916637953
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64039.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64039
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
