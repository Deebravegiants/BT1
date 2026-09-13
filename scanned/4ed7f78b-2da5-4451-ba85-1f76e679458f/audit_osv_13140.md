# [H] CVE-2018-17937

## Summary
Severity: High
Advisory: CVE-2018-17937
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-13
Source: https://osv.dev/vulnerability/CVE-2018-17937
Type: osv

## Details
gpsd versions 2.90 to 3.17 and microjson versions 1.0 to 1.3, an open source project, allow a stack-based buffer overflow, which may allow remote attackers to execute arbitrary code on embedded platforms via traffic on Port 2947/TCP or crafted JSON inputs.

## References
- http://www.securityfocus.com/bid/107029
- https://ics-cert.us-cert.gov/advisories/ICSA-18-310-01
- https://lists.debian.org/debian-lts-announce/2019/03/msg00040.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00024.html
- https://security.gentoo.org/glsa/202009-17
