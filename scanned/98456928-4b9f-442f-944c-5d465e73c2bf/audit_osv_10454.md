# [M] CVE-2017-15722

## Summary
Severity: Medium
Advisory: CVE-2017-15722
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-22
Source: https://osv.dev/vulnerability/CVE-2017-15722
Type: osv

## Details
In certain cases, Irssi before 1.0.5 may fail to verify that a Safe channel ID is long enough, causing reads beyond the end of the string.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00022.html
- https://www.debian.org/security/2017/dsa-4016
- http://openwall.com/lists/oss-security/2017/10/22/4
- https://irssi.org/security/irssi_sa_2017_10.txt
