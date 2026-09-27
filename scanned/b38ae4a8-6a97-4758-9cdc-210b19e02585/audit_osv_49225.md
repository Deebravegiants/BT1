# [M] CVE-2018-7170

## Summary
Severity: Medium
Advisory: CVE-2018-7170
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7170
Type: osv

## Details
ntpd in ntp 4.2.x before 4.2.8p7 and 4.3.x before 4.3.92 allows authenticated users that know the private symmetric key to create arbitrarily-many ephemeral associations in order to win the clock selection of ntpd and modify a victim's clock via a Sybil attack. This issue exists because of an incomplete fix for CVE-2016-1549.

## References
- http://packetstormsecurity.com/files/146631/Slackware-Security-Advisory-ntp-Updates.html
- http://support.ntp.org/bin/view/Main/NtpBug3415
- https://security.FreeBSD.org/advisories/FreeBSD-SA-18:02.ntp.asc
- https://security.gentoo.org/glsa/201805-12
- https://www.synology.com/support/security/Synology_SA_18_13
- http://www.securityfocus.com/archive/1/541824/100/0/threaded
- http://www.securityfocus.com/bid/103194
- https://security.netapp.com/advisory/ntap-20180626-0001/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03962en_us
- https://bugzilla.redhat.com/show_bug.cgi?id=1550214
