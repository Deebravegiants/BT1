# [H] CVE-2017-15091

## Summary
Severity: High
Advisory: CVE-2017-15091
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2017-15091
Type: osv

## Details
An issue has been found in the API component of PowerDNS Authoritative 4.x up to and including 4.0.4 and 3.x up to and including 3.4.11, where some operations that have an impact on the state of the server are still allowed even though the API has been configured as read-only via the api-readonly keyword. This missing check allows an attacker with valid API credentials to flush the cache, trigger a zone transfer or send a NOTIFY.

## References
- http://www.securityfocus.com/bid/101982
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2017-04.html
