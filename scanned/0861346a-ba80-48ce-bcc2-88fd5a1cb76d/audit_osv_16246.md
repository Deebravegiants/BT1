# [H] CVE-2019-3823

## Summary
Severity: High
Advisory: CVE-2019-3823
Aliases: CURL-CVE-2019-3823
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/CVE-2019-3823
Type: osv

## Details
libcurl versions from 7.34.0 to before 7.64.0 are vulnerable to a heap out-of-bounds read in the code handling the end-of-response for SMTP. If the buffer passed to `smtp_endofresp()` isn't NUL terminated and contains no character ending the parsed number, and `len` is set to 5, then the `strtol()` call reads beyond the allocated buffer. The read contents will not be returned to the caller.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-936080.pdf
- https://lists.apache.org/thread.html/8338a0f605bdbb3a6098bb76f666a95fc2b2f53f37fa1ecc89f1146f%40%3Cdevnull.infra.apache.org%3E
- http://www.securityfocus.com/bid/106950
- https://access.redhat.com/errata/RHSA-2019:3701
- https://security.gentoo.org/glsa/201903-03
- https://usn.ubuntu.com/3882-1/
- https://www.debian.org/security/2019/dsa-4386
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3823
- https://curl.haxx.se/docs/CVE-2019-3823.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://security.netapp.com/advisory/ntap-20190315-0001/
