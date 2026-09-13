# [H] drm/komeda: fix integer overflow in AFBC framebuffer size check

## Summary
Severity: High
Advisory: CVE-2026-53068
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53068
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/komeda: fix integer overflow in AFBC framebuffer size check

The AFBC framebuffer size validation calculates the minimum required
buffer size by adding the AFBC payload size to the framebuffer offset.
This addition is performed without checking for integer overflow.

If the addition oveflows, the size check may incorrectly succed and
allow userspace to provide an undersized drm_gem_object, potentially
leading to out-of-bounds memory access.

Add usage of check_add_overflow() to safely compute the minimum
required size and reject the framebuffer if an overflow is detected.
This makes the AFBC size validation more robust against malformed.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/02ff8a7d3d0eecc546b9ab4c07b3d7c65d485583
- https://git.kernel.org/stable/c/779ec12c85c9e4547519e3903a371a3b26a289de
- https://git.kernel.org/stable/c/8165e8b28fdf392c2c7412518d602b4f193812a8
- https://git.kernel.org/stable/c/872d923b852705054bc099af663da862fdc1097d
- https://git.kernel.org/stable/c/a3a2a9bdc0f9c2d863a5a290cb2d4a565f7268e7
- https://git.kernel.org/stable/c/d8a541906860aa3519b1874780d933c766918a7c
- https://git.kernel.org/stable/c/e27b58095d7d3ac72f230e318838dee956258460
- https://git.kernel.org/stable/c/fe1f80f8f6e8611ac6349b9d464e8750443390cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53068.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
