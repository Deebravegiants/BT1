# [H] CVE-2018-7182

## Summary
Severity: High
Advisory: CVE-2018-7182
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7182
Type: osv

## Details
The ctl_getitem method in ntpd in ntp-4.2.8p6 before 4.2.8p11 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted mode 6 packet with a ntpd instance from 4.2.8p6 through 4.2.8p10.

## References
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03962en_us
- https://security.netapp.com/advisory/ntap-20180626-0001/
- https://www.synology.com/support/security/Synology_SA_18_13
- http://support.ntp.org/bin/view/Main/NtpBug3412
- http://www.securityfocus.com/archive/1/541824/100/0/threaded
- http://www.securityfocus.com/bid/103191
- https://usn.ubuntu.com/3707-1/
- http://packetstormsecurity.com/files/146631/Slackware-Security-Advisory-ntp-Updates.html
- https://security.gentoo.org/glsa/201805-12
- https://security.FreeBSD.org/advisories/FreeBSD-SA-18:02.ntp.asc
- https://www.exploit-db.com/exploits/45846/
