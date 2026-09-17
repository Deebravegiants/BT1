# [H] CVE-2016-1548

## Summary
Severity: High
Advisory: CVE-2016-1548
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-1548
Type: osv

## Details
An attacker can spoof a packet from a legitimate ntpd server with an origin timestamp that matches the peer->dst timestamp recorded for that server. After making this switch, the client in NTP 4.2.8p4 and earlier and NTPSec aa48d001683e5b791a743ec9c575aaf7d867a2b0c will reject all future legitimate server responses. It is possible to force the victim client to move time after the mode has been changed. ntpq gives no indication that the mode has been switched.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2016-0082
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00114.html
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160428-ntpd
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/88264
- https://cert-portal.siemens.com/productcert/pdf/ssa-211752.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-497656.pdf
- http://www.securityfocus.com/archive/1/538233/100/0/threaded
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00001.html
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00020.html
- http://www.securityfocus.com/archive/1/archive/1/538233/100/0/threaded
- http://www.securitytracker.com/id/1035705
- https://www.kb.cert.org/vuls/id/718152
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184669.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183647.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00026.html
- http://packetstormsecurity.com/files/136864/Slackware-Security-Advisory-ntp-Updates.html
