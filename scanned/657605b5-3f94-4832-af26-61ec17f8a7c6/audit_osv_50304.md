# [H] CVE-2020-11868

## Summary
Severity: High
Advisory: CVE-2020-11868
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-17
Source: https://osv.dev/vulnerability/CVE-2020-11868
Type: osv

## Details
ntpd in ntp before 4.2.8p14 and 4.3.x before 4.3.100 allows an off-path attacker to block unauthenticated synchronization via a server mode packet with a spoofed source IP address, because transmissions are rescheduled even when a packet lacks a valid origin timestamp.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00044.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00004.html
- https://security.gentoo.org/glsa/202007-12
- https://security.netapp.com/advisory/ntap-20200424-0002/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00005.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1716665
- http://support.ntp.org/bin/view/Main/NtpBug3592
- https://www.oracle.com//security-alerts/cpujul2021.html
