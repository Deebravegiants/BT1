# [M] CVE-2017-9954

## Summary
Severity: Medium
Advisory: CVE-2017-9954
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-9954
Type: osv

## Details
The getvalue function in tekhex.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, allows remote attackers to cause a denial of service (stack-based buffer over-read and application crash) via a crafted tekhex file, as demonstrated by mishandling within the nm program.

## References
- http://www.securityfocus.com/bid/99307
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21670
