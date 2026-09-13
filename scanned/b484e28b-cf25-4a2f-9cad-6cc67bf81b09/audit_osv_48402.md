# [M] CVE-2017-7443

## Summary
Severity: Medium
Advisory: CVE-2017-7443
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-7443
Type: osv

## Details
apt-cacher before 1.7.15 and apt-cacher-ng before 3.4 allow HTTP response splitting via encoded newline characters, related to lack of blocking for the %0[ad] regular expression.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=858739
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=858833
