# [M] CVE-2015-1239

## Summary
Severity: Medium
Advisory: CVE-2015-1239
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2015-1239
Type: osv

## Details
Double free vulnerability in the j2k_read_ppm_v3 function in OpenJPEG before r2997, as used in PDFium in Google Chrome, allows remote attackers to cause a denial of service (process crash) via a crafted PDF.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00025.html
- https://bugs.chromium.org/p/chromium/issues/detail?id=430891
- https://bugs.chromium.org/p/chromium/issues/detail?id=457493
