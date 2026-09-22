# [H] CVE-2015-5300

## Summary
Severity: High
Advisory: CVE-2015-5300
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-21
Source: https://osv.dev/vulnerability/CVE-2015-5300
Type: osv

## Details
The panic_gate check in NTP before 4.2.8p5 is only re-enabled after the first change to the system clock that was greater than 128 milliseconds by default, which allows remote attackers to set NTP to an arbitrary time when started with the -g option, or to alter the time by up to 900 seconds otherwise by responding to an unspecified number of requests from trusted sources, and leveraging a resulting denial of service (abort and restart).

## References
- http://aix.software.ibm.com/aix/efixes/security/ntp_advisory5.asc
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/170684.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/170926.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177507.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00048.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00042.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00114.html
- http://rhn.redhat.com/errata/RHSA-2015-1930.html
- http://seclists.org/bugtraq/2016/Feb/164
- http://support.ntp.org/bin/view/Main/NtpBug2956
- http://support.ntp.org/bin/view/Main/SecurityNotice#January_2016_NTP_4_2_8p5_Securit
- http://www.debian.org/security/2015/dsa-3388
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.securityfocus.com/bid/77312
- http://www.securitytracker.com/id/1034670
