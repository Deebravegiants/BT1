# [M] CVE-2017-6463

## Summary
Severity: Medium
Advisory: CVE-2017-6463
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-6463
Type: osv

## Details
NTP before 4.2.8p10 and 4.3.x before 4.3.94 allows remote authenticated users to cause a denial of service (daemon crash) via an invalid setting in a :config directive, related to the unpeer option.

## References
- https://usn.ubuntu.com/3707-2/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03962en_us
- https://support.apple.com/HT208144
- http://support.ntp.org/bin/view/Main/SecurityNotice#March_2017_ntp_4_2_8p10_NTP_Secu
- http://www.securitytracker.com/id/1038123
- https://access.redhat.com/errata/RHSA-2017:3071
- http://support.ntp.org/bin/view/Main/NtpBug3387
- http://www.securityfocus.com/bid/97049
- https://access.redhat.com/errata/RHSA-2018:0855
- https://security.FreeBSD.org/advisories/FreeBSD-SA-17:03.ntp.asc
