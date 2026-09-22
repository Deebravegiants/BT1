# [M] CVE-2016-3992

## Summary
Severity: Medium
Advisory: CVE-2016-3992
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-07-26
Source: https://osv.dev/vulnerability/CVE-2016-3992
Type: osv

## Details
cronic before 3 allows local users to write to arbitrary files via a symlink attack on a (1) cronic.out.$$, (2) cronic.err.$$, or (3) cronic.trace.$$ file in /tmp.

## References
- http://www.openwall.com/lists/oss-security/2016/04/09/4
- http://www.openwall.com/lists/oss-security/2016/04/10/2
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00013.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=820331
