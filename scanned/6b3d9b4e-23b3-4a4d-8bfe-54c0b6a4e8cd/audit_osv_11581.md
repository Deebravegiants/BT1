# [M] CVE-2017-8842

## Summary
Severity: Medium
Advisory: CVE-2017-8842
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2017-8842
Type: osv

## Details
The bufRead::get() function in libzpaq/libzpaq.h in liblrzip.so in lrzip 0.631 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted archive.

## References
- https://blogs.gentoo.org/ago/2017/05/07/lrzip-divide-by-zero-in-bufreadget-libzpaq-h/
- https://security.gentoo.org/glsa/202005-01
- https://github.com/ckolivas/lrzip/issues/66
