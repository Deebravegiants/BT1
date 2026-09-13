# [M] CVE-2016-7525

## Summary
Severity: Medium
Advisory: CVE-2016-7525
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7525
Type: osv

## Details
Heap-based buffer overflow in coders/psd.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted PSD file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1537424
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378757
- https://github.com/ImageMagick/ImageMagick/commit/5f16640725b1225e6337c62526e6577f0f88edb8
- https://github.com/ImageMagick/ImageMagick/issues/98
