# [H] drm/vmwgfx: validate external BO copy bounds for both stride paths

## Summary
Severity: High
Advisory: CVE-2026-80700
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80700
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.151, >=6.7.0 <6.12.103, >=6.11.0 <6.18.44, >=6.13.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: validate external BO copy bounds for both stride paths

vmw_external_bo_copy() trusts caller-supplied offsets, strides, and
heights and operates on imported dma-buf vmaps:

  - The equal-stride memcpy() bound was clamped after subtracting the
    offsets from dst_size and src_size; an offset larger than the BO
    size wraps the unsigned subtraction to a huge value and the
    resulting memcpy() runs off the end of the vmap.  dst_stride *
    height is also a u32 multiplication that can overflow.
  - The non-equal-stride row-by-row path had no bound at all.  The
    loop touches bytes through offset + (height - 1) * stride +
    width_in_bytes, with only a WARN_ON(dst_stride < width_in_bytes),
    and could likewise step past the end of either mapping.

The offsets and strides are derived from STDU/SOU plane state, so a
configured CRTC submitting a crafted atomic commit on an imported
framebuffer can reach this path.

Validate the exact row-copy endpoint against each BO's size up front
using check_mul_overflow() and check_add_overflow().  Use the bulk
memcpy() path only when width_in_bytes covers the whole stride;
otherwise copy one row at a time so partial-row updates near the bottom
of a framebuffer remain valid.  Also reject zero strides and stride <
width_in_bytes, both of which the row-by-row path cannot represent
safely.

## References
- https://git.kernel.org/stable/c/042ca38779554687fc32b66a28328e0d9a36c58f
- https://git.kernel.org/stable/c/4e0f669e2951b742239c6fe847fcc406fe78748d
- https://git.kernel.org/stable/c/5e4a2d15637a906cbd9bc98e0bf969f5f713e344
- https://git.kernel.org/stable/c/706c93c5813caabbb0d0a576c017d15aeec2c113
- https://git.kernel.org/stable/c/e7b25a6011781ebfdbc458552cae6d4156732771
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80700.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80700
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
