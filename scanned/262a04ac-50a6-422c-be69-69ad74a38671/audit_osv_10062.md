# [M] CVE-2017-12967

## Summary
Severity: Medium
Advisory: CVE-2017-12967
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-19
Source: https://osv.dev/vulnerability/CVE-2017-12967
Type: osv

## Details
The getsym function in tekhex.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (stack-based buffer over-read and application crash) via a malformed tekhex binary.

## References
- http://www.securityfocus.com/bid/100462
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=21962
