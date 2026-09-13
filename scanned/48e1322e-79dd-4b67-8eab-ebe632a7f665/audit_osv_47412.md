# [H] CVE-2016-4954

## Summary
Severity: High
Advisory: CVE-2016-4954
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-07-05
Source: https://osv.dev/vulnerability/CVE-2016-4954
Type: osv

## Details
The process_packet function in ntp_proto.c in ntpd in NTP 4.x before 4.2.8p8 allows remote attackers to cause a denial of service (peer-variable modification) by sending spoofed packets from many source IP addresses in a certain scenario, as demonstrated by triggering an incorrect leap indication.

## References
- http://www.securityfocus.com/archive/1/archive/1/538599/100/0/threaded
- http://www.securityfocus.com/archive/1/archive/1/540683/100/0/threaded
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00042.html
- http://www.securityfocus.com/archive/1/538600/100/0/threaded
- https://www.kb.cert.org/vuls/id/321640
- http://packetstormsecurity.com/files/137322/FreeBSD-Security-Advisory-FreeBSD-SA-16-24.ntp.html
- http://www.securityfocus.com/archive/1/538599/100/0/threaded
- http://www.securityfocus.com/archive/1/540683/100/0/threaded
- http://www.securityfocus.com/archive/1/archive/1/538600/100/0/threaded
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160603-ntpd
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ORAMN3Q7TVJ54MBYF75XCJOE3DP7LYHT/
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K3EYJQHJZ2KTVQ7ICEFHXTLZ36MRASWX/
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WNWGCQLW2VY72NIUYMJOCAKJKTXHDUK2/
- http://packetstormsecurity.com/files/137321/Slackware-Security-Advisory-ntp-Updates.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-497656.pdf
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:24.ntp.asc
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00018.html
- http://www.ubuntu.com/usn/USN-3096-1
