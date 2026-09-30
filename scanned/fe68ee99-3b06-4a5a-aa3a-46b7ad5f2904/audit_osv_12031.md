# [C] CVE-2018-1000810

## Summary
Severity: Critical
Advisory: CVE-2018-1000810
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-08
Source: https://osv.dev/vulnerability/CVE-2018-1000810
Type: osv

## Details
The Rust Programming Language Standard Library version 1.29.0, 1.28.0, 1.27.2, 1.27.1, 127.0, 126.2, 126.1, 126.0 contains a CWE-680: Integer Overflow to Buffer Overflow vulnerability in standard library that can result in buffer overflow. This attack appear to be exploitable via str::repeat, passed a large number, can overflow an internal buffer. This vulnerability appears to have been fixed in 1.29.1.

## References
- https://groups.google.com/forum/#%21topic/rustlang-security-announcements/CmSuTm-SaU0
- https://blog.rust-lang.org/2018/09/21/Security-advisory-for-std.html
- https://security.gentoo.org/glsa/201812-11
