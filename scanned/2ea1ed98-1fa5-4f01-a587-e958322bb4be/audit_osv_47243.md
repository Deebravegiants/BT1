# [M] CVE-2016-1923

## Summary
Severity: Medium
Advisory: CVE-2016-1923
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-27
Source: https://osv.dev/vulnerability/CVE-2016-1923
Type: osv

## Details
Heap-based buffer overflow in the opj_j2k_update_image_data function in OpenJpeg 2016.1.18 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted JPEG 2000 image.

## References
- http://www.openwall.com/lists/oss-security/2016/01/18/4
- http://www.openwall.com/lists/oss-security/2016/01/18/7
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://security.gentoo.org/glsa/201612-26
