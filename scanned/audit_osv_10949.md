# [M] CVE-2017-5361

## Summary
Severity: Medium
Advisory: CVE-2017-5361
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-03
Source: https://osv.dev/vulnerability/CVE-2017-5361
Type: osv

## Details
Request Tracker (RT) 4.x before 4.0.25, 4.2.x before 4.2.14, and 4.4.x before 4.4.2 does not use a constant-time comparison algorithm for secrets, which makes it easier for remote attackers to obtain sensitive user password information via a timing side-channel attack.

## References
- http://www.debian.org/security/2017/dsa-3882
- http://www.debian.org/security/2017/dsa-3883
- https://forum.bestpractical.com/t/security-vulnerabilities-in-rt-2017-06-15/32016
