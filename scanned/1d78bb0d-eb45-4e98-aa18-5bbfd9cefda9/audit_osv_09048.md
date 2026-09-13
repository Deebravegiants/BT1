# [M] CVE-2016-7521

## Summary
Severity: Medium
Advisory: CVE-2016-7521
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7521
Type: osv

## Details
Heap-based buffer overflow in coders/psd.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted PSD file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1537418
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378748
- https://github.com/ImageMagick/ImageMagick/commit/30eec879c8b446b0ea9a3bb0da1a441cc8482bc4
- https://github.com/ImageMagick/ImageMagick/issues/92
