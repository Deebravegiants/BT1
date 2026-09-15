# [M] CVE-2015-5146

## Summary
Severity: Medium
Advisory: CVE-2015-5146
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-24
Source: https://osv.dev/vulnerability/CVE-2015-5146
Type: osv

## Details
ntpd in ntp before 4.2.8p3 with remote configuration enabled allows remote authenticated users with knowledge of the configuration password and access to a computer entrusted to perform remote configuration to cause a denial of service (service crash) via a NULL byte in a crafted configuration directive packet.

## References
- http://bugs.ntp.org/show_bug.cgi?id=2853
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/170926.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/169167.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/166992.html
- http://support.ntp.org/bin/view/Main/SecurityNotice#March_2017_ntp_4_2_8p10_NTP_Secu
- http://www.debian.org/security/2015/dsa-3388
- http://www.securityfocus.com/bid/75589
- http://www.securitytracker.com/id/1034168
- https://bugzilla.redhat.com/show_bug.cgi?id=1238136
- https://security.gentoo.org/glsa/201509-01
- https://security.netapp.com/advisory/ntap-20180731-0003/
- http://bugs.ntp.org/show_bug.cgi?id=2853
- https://bugzilla.redhat.com/show_bug.cgi?id=1238136
