# [H] CVE-2017-9113

## Summary
Severity: High
Advisory: CVE-2017-9113
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-21
Source: https://osv.dev/vulnerability/CVE-2017-9113
Type: osv

## Details
In OpenEXR 2.2.0, an invalid write of size 1 in the bufferedReadPixels function in ImfInputFile.cpp could cause the application to crash or execute arbitrary code.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00000.html
- https://github.com/openexr/openexr/releases/tag/v2.2.1
- https://lists.debian.org/debian-lts-announce/2020/08/msg00056.html
- https://usn.ubuntu.com/4148-1/
- https://usn.ubuntu.com/4339-1/
- http://www.openwall.com/lists/oss-security/2017/05/12/5
- https://www.debian.org/security/2020/dsa-4755
- https://github.com/openexr/openexr/issues/232
- https://github.com/openexr/openexr/pull/233
