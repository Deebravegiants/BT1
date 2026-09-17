# [H] CVE-2020-13817

## Summary
Severity: High
Advisory: CVE-2020-13817
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/CVE-2020-13817
Type: osv

## Details
ntpd in ntp before 4.2.8p14 and 4.3.x before 4.3.100 allows remote attackers to cause a denial of service (daemon exit or system time change) by predicting transmit timestamps for use in spoofed packets. The victim must be relying on unauthenticated IPv4 time sources. There must be an off-path attacker who can query time from the victim's ntpd instance.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00044.html
- http://support.ntp.org/bin/view/Main/NtpBug3596
- https://security.gentoo.org/glsa/202007-12
- https://security.netapp.com/advisory/ntap-20200625-0004/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00005.html
- https://bugs.ntp.org/show_bug.cgi?id=3596
- https://www.oracle.com/security-alerts/cpujan2022.html
