# [H] drm/fb-helper: Fix out-of-bounds access

## Summary
Severity: High
Advisory: CVE-2022-50221
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50221
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/fb-helper: Fix out-of-bounds access

Clip memory range to screen-buffer size to avoid out-of-bounds access
in fbdev deferred I/O's damage handling.

Fbdev's deferred I/O can only track pages. From the range of pages, the
damage handler computes the clipping rectangle for the display update.
If the fbdev screen buffer ends near the beginning of a page, that page
could contain more scanlines. The damage handler would then track these
non-existing scanlines as dirty and provoke an out-of-bounds access
during the screen update. Hence, clip the maximum memory range to the
size of the screen buffer.

While at it, rename the variables min/max to min_off/max_off in
drm_fb_helper_deferred_io(). This avoids confusion with the macros of
the same name.

## References
- https://git.kernel.org/stable/c/9c49ac792c639dbec0728b513329a32461f72253
- https://git.kernel.org/stable/c/ae25885bdf59fde40726863c57fd20e4a0642183
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50221.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50221
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
