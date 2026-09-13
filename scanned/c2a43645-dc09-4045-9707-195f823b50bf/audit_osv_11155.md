# [M] CVE-2017-6418

## Summary
Severity: Medium
Advisory: CVE-2017-6418
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-6418
Type: osv

## Details
libclamav/message.c in ClamAV 0.99.2 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted e-mail message.

## References
- http://www.securityfocus.com/bid/100154
- https://github.com/varsleak/varsleak-vul/blob/master/clamav-vul/heap-overflow/clamav_email_crash.md
- https://security.gentoo.org/glsa/201804-16
- https://bugzilla.clamav.net/show_bug.cgi?id=11797
- https://github.com/vrtadmin/clamav-devel/commit/586a5180287262070637c8943f2f7efd652e4a2c
