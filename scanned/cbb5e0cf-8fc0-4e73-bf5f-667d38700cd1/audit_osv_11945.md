# [H] CVE-2018-1000168

## Summary
Severity: High
Advisory: CVE-2018-1000168
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-08
Source: https://osv.dev/vulnerability/CVE-2018-1000168
Type: osv

## Details
nghttp2 version >= 1.10.0 and nghttp2 <= v1.31.0 contains an Improper Input Validation CWE-20 vulnerability in ALTSVC frame handling that can result in segmentation fault leading to denial of service. This attack appears to be exploitable via network client. This vulnerability appears to have been fixed in >= 1.31.1.

## References
- http://www.securityfocus.com/bid/103952
- https://access.redhat.com/errata/RHSA-2019:0366
- https://access.redhat.com/errata/RHSA-2019:0367
- https://lists.debian.org/debian-lts-announce/2021/10/msg00011.html
- https://nghttp2.org/blog/2018/04/12/nghttp2-v1-31-1/
- https://nodejs.org/en/blog/vulnerability/june-2018-security-releases/
