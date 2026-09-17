# [H] drm/amd/display: Check num_valid_sets before accessing reader_wm_sets[]

## Summary
Severity: High
Advisory: CVE-2024-46815
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46815
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.109, >=6.2.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Check num_valid_sets before accessing reader_wm_sets[]

[WHY & HOW]
num_valid_sets needs to be checked to avoid a negative index when
accessing reader_wm_sets[num_valid_sets - 1].

This fixes an OVERRUN issue reported by Coverity.

## References
- https://git.kernel.org/stable/c/21f9cb44f8c60bf6c26487d428b1a09ad3e8aebf
- https://git.kernel.org/stable/c/6a4a08e45e614cfa7a56498cdfaeb7fae2f07fa0
- https://git.kernel.org/stable/c/7c47dd2e92341f2989ab73dbed07f8894593ad7b
- https://git.kernel.org/stable/c/a72d4996409569027b4609414a14a87679b12267
- https://git.kernel.org/stable/c/b36e9b3104c4ba0f2f5dd083dcf6159cb316c996
- https://git.kernel.org/stable/c/b38a4815f79b87efb196cd5121579fc51e29a7fb
- https://git.kernel.org/stable/c/c4a7f7c0062fe2c73f70bb7e335199e25bd71492
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46815.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46815
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
