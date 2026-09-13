# [M] CVE-2017-10794

## Summary
Severity: Medium
Advisory: CVE-2017-10794
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-02
Source: https://osv.dev/vulnerability/CVE-2017-10794
Type: osv

## Details
When GraphicsMagick 1.3.25 processes an RGB TIFF picture (with metadata indicating a single sample per pixel) in coders/tiff.c, a buffer overflow occurs, related to QuantumTransferMode.

## References
- https://usn.ubuntu.com/4206-1/
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/99355
- https://sourceforge.net/p/graphicsmagick/code/ci/a20bee0a0ad216aa11a2be3de63b60ca6bef4106/
