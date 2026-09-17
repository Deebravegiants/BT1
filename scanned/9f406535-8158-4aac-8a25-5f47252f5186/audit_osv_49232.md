# [H] CVE-2018-7185

## Summary
Severity: High
Advisory: CVE-2018-7185
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7185
Type: osv

## Details
The protocol engine in ntp 4.2.6 before 4.2.8p11 allows a remote attackers to cause a denial of service (disruption) by continually sending a packet with a zero-origin timestamp and source IP address of the "other side" of an interleaved association causing the victim ntpd to reset its association.

## References
- https://security.gentoo.org/glsa/201805-12
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03962en_us
- https://usn.ubuntu.com/3707-1/
- https://usn.ubuntu.com/3707-2/
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://www.synology.com/support/security/Synology_SA_18_13
- http://packetstormsecurity.com/files/146631/Slackware-Security-Advisory-ntp-Updates.html
- http://support.ntp.org/bin/view/Main/NtpBug3454
- http://www.securityfocus.com/archive/1/541824/100/0/threaded
- http://www.securityfocus.com/bid/103339
- https://security.FreeBSD.org/advisories/FreeBSD-SA-18:02.ntp.asc
- https://security.netapp.com/advisory/ntap-20180626-0001/
