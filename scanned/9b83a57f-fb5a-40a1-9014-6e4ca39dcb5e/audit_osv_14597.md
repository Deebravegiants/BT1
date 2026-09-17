# [M] CVE-2019-10203

## Summary
Severity: Medium
Advisory: CVE-2019-10203
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-11-22
Source: https://osv.dev/vulnerability/CVE-2019-10203
Type: osv

## Details
PowerDNS Authoritative daemon , pdns versions 4.0.x before 4.0.9, 4.1.x before 4.1.11, exiting when encountering a serial between 2^31 and 2^32-1 while trying to notify a slave leads to DoS.

## References
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2019-06.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10203
