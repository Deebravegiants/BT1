# [M] CVE-2020-15025

## Summary
Severity: Medium
Advisory: CVE-2020-15025
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-24
Source: https://osv.dev/vulnerability/CVE-2020-15025
Type: osv

## Details
ntpd in ntp 4.2.8 before 4.2.8p15 and 4.3.x before 4.3.101 allows remote attackers to cause a denial of service (memory consumption) by sending packets, because memory is not freed in situations where a CMAC key is used and associated with a CMAC algorithm in the ntp.keys file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00044.html
- https://security.gentoo.org/glsa/202007-12
- https://security.netapp.com/advisory/ntap-20200702-0002/
- https://support.ntp.org/bin/view/Main/NtpBug3661
- https://support.ntp.org/bin/view/Main/SecurityNotice#June_2020_ntp_4_2_8p15_NTP_Relea
- https://bugs.gentoo.org/729458
- https://www.oracle.com/security-alerts/cpujan2021.html
