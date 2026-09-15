# [H] media: atomisp: prevent integer overflow in sh_css_set_black_frame()

## Summary
Severity: High
Advisory: CVE-2022-50399
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50399
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.18, >=5.8.0 <5.15.77, >=5.16.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: atomisp: prevent integer overflow in sh_css_set_black_frame()

The "height" and "width" values come from the user so the "height * width"
multiplication can overflow.

## References
- https://git.kernel.org/stable/c/3ad290194bb06979367622e47357462836c1d3b4
- https://git.kernel.org/stable/c/51b8dc5163d2ff2bf04019f8bf7e3bd0e75bb654
- https://git.kernel.org/stable/c/a549517e4b761f3940011db30320cb8c9badde54
- https://git.kernel.org/stable/c/a560aeac2f2d284903b5900774765d7fc61547bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50399.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50399
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
