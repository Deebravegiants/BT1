# [M] CVE-2021-3272

## Summary
Severity: Medium
Advisory: CVE-2021-3272
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-01-27
Source: https://osv.dev/vulnerability/CVE-2021-3272
Type: osv

## Details
jp2_decode in jp2/jp2_dec.c in libjasper in JasPer 2.0.24 has a heap-based buffer over-read when there is an invalid relationship between the number of channels and the number of image components.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4BZFU2F6UW4L2FJE65WJLWGUIELDWCL7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HD2Y2LT4N5ZWCMKYCUIKB3XODNJLOW3J/
- https://github.com/jasper-software/jasper/issues/259
