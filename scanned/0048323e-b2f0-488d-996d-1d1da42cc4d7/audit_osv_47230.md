# [M] CVE-2016-1549

## Summary
Severity: Medium
Advisory: CVE-2016-1549
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-1549
Type: osv

## Details
A malicious authenticated peer can create arbitrarily-many ephemeral associations in order to win the clock selection algorithm in ntpd in NTP 4.2.8p4 and earlier and NTPsec 3e160db8dc248a0bcb053b56a80167dc742d2b74 and a5fb34b9cc89b92a8fef2f459004865c93bb7f92 and modify a victim's clock.

## References
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03962en_us
- https://www.synology.com/support/security/Synology_SA_18_13
- http://www.securityfocus.com/bid/88200
- http://www.securitytracker.com/id/1035705
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- https://security.netapp.com/advisory/ntap-20171004-0002/
- http://www.talosintelligence.com/reports/TALOS-2016-0083/
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:16.ntp.asc
- https://security.gentoo.org/glsa/201607-15
