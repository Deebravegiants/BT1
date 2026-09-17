# [H] drivers:md:fix a potential use-after-free bug

## Summary
Severity: High
Advisory: CVE-2022-50022
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50022
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.9.326, >=4.10.0 <4.14.291, >=4.15.0 <4.19.256, >=4.20.0 <5.4.211, >=5.5.0 <5.10.138, >=5.11.0 <5.15.63, >=5.16.0 <5.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers:md:fix a potential use-after-free bug

In line 2884, "raid5_release_stripe(sh);" drops the reference to sh and
may cause sh to be released. However, sh is subsequently used in lines
2886 "if (sh->batch_head && sh != sh->batch_head)". This may result in an
use-after-free bug.

It can be fixed by moving "raid5_release_stripe(sh);" to the bottom of
the function.

## References
- https://git.kernel.org/stable/c/09cf99bace7789d91caa8d10fbcfc8b2fb35857f
- https://git.kernel.org/stable/c/104212471b1c1817b311771d817fb692af983173
- https://git.kernel.org/stable/c/5d8325fd15892c8ab1146edc1d7ed8463de39636
- https://git.kernel.org/stable/c/7470a4314b239e9a9580f248fdf4c9a92805490e
- https://git.kernel.org/stable/c/d9b94c3ace549433de8a93eeb27b0391fc8ac406
- https://git.kernel.org/stable/c/e5b3dd2d92c4511e81f6e4ec9c5bb7ad25e03d13
- https://git.kernel.org/stable/c/eb3a4f73f43f839df981dda5859e8e075067a360
- https://git.kernel.org/stable/c/f5d46f1b47f65da1faf468277b261eb78c8e25b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50022.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50022
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
