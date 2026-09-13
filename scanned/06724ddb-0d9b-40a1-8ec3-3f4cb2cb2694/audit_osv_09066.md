# [M] CVE-2016-7540

## Summary
Severity: Medium
Advisory: CVE-2016-7540
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7540
Type: osv

## Details
coders/rgf.c in ImageMagick before 6.9.4-10 allows remote attackers to cause a denial of service (assertion failure) by converting an image to rgf format.

## References
- http://www.securityfocus.com/bid/93228
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1594060
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378777
- https://github.com/ImageMagick/ImageMagick/commit/a0108a892f9ea3c2bb1e7a49b7d71376c2ecbff7
- https://github.com/ImageMagick/ImageMagick/pull/223
