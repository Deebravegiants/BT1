# [M] CVE-2015-7850

## Summary
Severity: Medium
Advisory: CVE-2015-7850
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2015-7850
Type: osv

## Details
ntpd in NTP 4.2.x before 4.2.8p4, and 4.3.x before 4.3.77 allows remote authenticated users to cause a denial of service (infinite loop or crash) by pointing the key file at the log file.

## References
- http://support.ntp.org/bin/view/Main/NtpBug2917
- http://www.debian.org/security/2015/dsa-3388
- http://www.securityfocus.com/bid/77279
- http://www.securitytracker.com/id/1033951
- https://bugzilla.redhat.com/show_bug.cgi?id=1274258
- https://security.gentoo.org/glsa/201607-15
- https://security.netapp.com/advisory/ntap-20171004-0001/
- http://support.ntp.org/bin/view/Main/NtpBug2917
- https://bugzilla.redhat.com/show_bug.cgi?id=1274258
