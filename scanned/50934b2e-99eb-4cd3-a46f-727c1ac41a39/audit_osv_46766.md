# [M] CVE-2015-1853

## Summary
Severity: Medium
Advisory: CVE-2015-1853
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-09
Source: https://osv.dev/vulnerability/CVE-2015-1853
Type: osv

## Details
chrony before 1.31.1 does not properly protect state variables in authenticated symmetric NTP associations, which allows remote attackers with knowledge of NTP peering to cause a denial of service (inability to synchronize) via random timestamps in crafted NTP data packets.

## References
- http://chrony.tuxfamily.org/News.html
- https://security.gentoo.org/glsa/201507-01
