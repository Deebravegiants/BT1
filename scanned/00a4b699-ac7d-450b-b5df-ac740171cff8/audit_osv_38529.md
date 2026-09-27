# [C] SAIL has heap buffer overflow in PSD decoder — bpp mismatch in LAB 16-bit mode

## Summary
Severity: Critical
Advisory: CVE-2026-40493
Aliases: GHSA-rcqx-gc76-r9mv
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-40493
Type: osv

## Details
SAIL is a cross-platform library for loading and saving images with support for animation, metadata, and ICC profiles. Prior to commit c930284445ea3ff94451ccd7a57c999eca3bc979, the PSD codec computes bytes-per-pixel (`bpp`) from raw header fields `channels * depth`, but the pixel buffer is allocated based on the resolved pixel format. For LAB mode with `channels=3, depth=16`, `bpp = (3*16+7)/8 = 6`, but the format `BPP40_CIE_LAB` allocates only 5 bytes per pixel. Every pixel write overshoots, causing a deterministic heap buffer overflow on every row. Commit c930284445ea3ff94451ccd7a57c999eca3bc979 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40493.json
- https://github.com/HappySeaFox/sail/security/advisories/GHSA-rcqx-gc76-r9mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-40493
- https://github.com/HappySeaFox/sail/commit/c930284445ea3ff94451ccd7a57c999eca3bc979
