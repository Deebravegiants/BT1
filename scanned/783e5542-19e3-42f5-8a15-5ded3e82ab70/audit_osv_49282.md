# [M] CVE-2018-8956

## Summary
Severity: Medium
Advisory: CVE-2018-8956
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-05-06
Source: https://osv.dev/vulnerability/CVE-2018-8956
Type: osv

## Details
ntpd in ntp 4.2.8p10, 4.2.8p11, 4.2.8p12 and 4.2.8p13 allow remote attackers to prevent a broadcast client from synchronizing its clock with a broadcast NTP server via soofed mode 3 and mode 5 packets. The attacker must either be a part of the same broadcast network or control a slave in that broadcast network that can capture certain required packets on the attacker's behalf and send them to the attacker.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00044.html
- http://www.ntp.org/
- https://arxiv.org/abs/2005.01783
- https://nikhiltripathi.in/NTP_attack.pdf
- https://security.netapp.com/advisory/ntap-20200518-0006/
- https://tools.ietf.org/html/rfc5905
