# [M] CVE-2016-7074

## Summary
Severity: Medium
Advisory: CVE-2016-7074
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-11
Source: https://osv.dev/vulnerability/CVE-2016-7074
Type: osv

## Details
An issue has been found in PowerDNS before 3.4.11 and 4.0.2, and PowerDNS recursor before 4.0.4, allowing an attacker in position of man-in-the-middle to alter the content of an AXFR because of insufficient validation of TSIG signatures. A missing check that the TSIG record is the last one, leading to the possibility of parsing records that are not covered by the TSIG signature.

## References
- https://doc.powerdns.com/md/security/powerdns-advisory-2016-04/
- https://www.debian.org/security/2017/dsa-3764
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-7074
