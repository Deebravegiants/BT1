# [H] fbdev: Add bounds checking in bit_putcs to fix vmalloc-out-of-bounds

## Summary
Severity: High
Advisory: CVE-2025-40304
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40304
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: Add bounds checking in bit_putcs to fix vmalloc-out-of-bounds

Add bounds checking to prevent writes past framebuffer boundaries when
rendering text near screen edges. Return early if the Y position is off-screen
and clip image height to screen boundary. Break from the rendering loop if the
X position is off-screen. When clipping image width to fit the screen, update
the character count to match the clipped width to prevent buffer size
mismatches.

Without the character count update, bit_putcs_aligned and bit_putcs_unaligned
receive mismatched parameters where the buffer is allocated for the clipped
width but cnt reflects the original larger count, causing out-of-bounds writes.

## References
- https://git.kernel.org/stable/c/15ba9acafb0517f8359ca30002c189a68ddbb939
- https://git.kernel.org/stable/c/1943b69e87b0ab35032d47de0a7fca9a3d1d6fc1
- https://git.kernel.org/stable/c/2d1359e11674ed4274934eac8a71877ae5ae7bbb
- https://git.kernel.org/stable/c/3637d34b35b287ab830e66048841ace404382b67
- https://git.kernel.org/stable/c/86df8ade88d290725554cefd03101ecd0fbd3752
- https://git.kernel.org/stable/c/996bfaa7372d6718b6d860bdf78f6618e850c702
- https://git.kernel.org/stable/c/ebc0730b490c7f27340b1222e01dd106e820320d
- https://git.kernel.org/stable/c/f0982400648a3e00580253e0c48e991f34d2684c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40304.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40304
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
