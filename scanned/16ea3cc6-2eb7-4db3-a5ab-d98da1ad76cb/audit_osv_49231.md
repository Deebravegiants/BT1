# [H] CVE-2018-7184

## Summary
Severity: High
Advisory: CVE-2018-7184
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7184
Type: osv

## Details
ntpd in ntp 4.2.8p4 before 4.2.8p11 drops bad packets before updating the "received" timestamp, which allows remote attackers to cause a denial of service (disruption) by sending a packet with a zero-origin timestamp causing the association to reset and setting the contents of the packet as the most recent timestamp. This issue is a result of an incomplete fix for CVE-2015-7704.

## References
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03962en_us
- http://support.ntp.org/bin/view/Main/NtpBug3453
- http://www.securityfocus.com/archive/1/541824/100/0/threaded
- http://www.securityfocus.com/bid/103192
- https://security.netapp.com/advisory/ntap-20180626-0001/
- https://usn.ubuntu.com/3707-1/
- http://packetstormsecurity.com/files/146631/Slackware-Security-Advisory-ntp-Updates.html
- https://security.FreeBSD.org/advisories/FreeBSD-SA-18:02.ntp.asc
- https://security.gentoo.org/glsa/201805-12
- https://www.synology.com/support/security/Synology_SA_18_13
