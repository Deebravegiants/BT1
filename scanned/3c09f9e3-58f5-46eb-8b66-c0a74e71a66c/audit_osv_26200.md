# [H] drm: Don't unref the same fb many times by mistake due to deadlock handling

## Summary
Severity: High
Advisory: CVE-2023-52486
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52486
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: Don't unref the same fb many times by mistake due to deadlock handling

If we get a deadlock after the fb lookup in drm_mode_page_flip_ioctl()
we proceed to unref the fb and then retry the whole thing from the top.
But we forget to reset the fb pointer back to NULL, and so if we then
get another error during the retry, before the fb lookup, we proceed
the unref the same fb again without having gotten another reference.
The end result is that the fb will (eventually) end up being freed
while it's still in use.

Reset fb to NULL once we've unreffed it to avoid doing it again
until we've done another fb lookup.

This turned out to be pretty easy to hit on a DG2 when doing async
flips (and CONFIG_DEBUG_WW_MUTEX_SLOWPATH=y). The first symptom I
saw that drm_closefb() simply got stuck in a busy loop while walking
the framebuffer list. Fortunately I was able to convince it to oops
instead, and from there it was easier to track down the culprit.

## References
- https://git.kernel.org/stable/c/376e21a9e4c2c63ee5d8d3aa74be5082c3882229
- https://git.kernel.org/stable/c/62f2e79cf9f4f47cc9dea9cebdf58d9f7b5695e0
- https://git.kernel.org/stable/c/9dd334a8245011ace45e53298175c7b659edb3e7
- https://git.kernel.org/stable/c/b4af63da9d94986c529d74499fdfe44289acd551
- https://git.kernel.org/stable/c/bfd0feb1b109cb63b87fdcd00122603787c75a1a
- https://git.kernel.org/stable/c/cb4daf271302d71a6b9a7c01bd0b6d76febd8f0c
- https://git.kernel.org/stable/c/d7afdf360f4ac142832b098b4de974e867cc063c
- https://git.kernel.org/stable/c/f55261469be87c55df13db76dc945f6bcd825105
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52486.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52486
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
