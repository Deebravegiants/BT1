# [M] Integer overflow in libvpx

## Summary
Severity: Medium
Advisory: CVE-2024-5197
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:L/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2024-06-03
Source: https://osv.dev/vulnerability/CVE-2024-5197
Type: osv

## Details
There exists interger overflows in libvpx in versions prior to 1.14.1. Calling vpx_img_alloc() with a large value of the d_w, d_h, or align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned vpx_image_t struct may be invalid. Calling vpx_img_wrap() with a large value of the d_w, d_h, or stride_align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned vpx_image_t struct may be invalid. We recommend upgrading to version 1.14.1 or beyond

## References
- https://chromium.googlesource.com
- https://chromium.googlesource.com/webm/
- https://g-issues.chromium.org/issues/332382766
- https://lists.debian.org/debian-lts-announce/2024/06/msg00005.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5197.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5197
