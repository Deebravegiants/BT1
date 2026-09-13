# [M] CVE-2017-12923

## Summary
Severity: Medium
Advisory: CVE-2017-12923
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-28
Source: https://osv.dev/vulnerability/CVE-2017-12923
Type: osv

## Details
OLEStream::WriteVT_LPSTR in olestrm.cpp in libfpx 1.3.1_p6 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted fpx image.

## References
- http://www.openwall.com/lists/oss-security/2017/08/17/9
- https://blogs.gentoo.org/ago/2017/08/09/libfpx-null-pointer-dereference-in-olestreamwritevt_lpstr-olestrm-cpp/
