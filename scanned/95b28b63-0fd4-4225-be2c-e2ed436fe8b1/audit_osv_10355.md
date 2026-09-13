# [M] CVE-2017-15093

## Summary
Severity: Medium
Advisory: CVE-2017-15093
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2017-15093
Type: osv

## Details
When api-config-dir is set to a non-empty value, which is not the case by default, the API in PowerDNS Recursor 4.x up to and including 4.0.6 and 3.x up to and including 3.7.4 allows an authorized user to update the Recursor's ACL by adding and removing netmasks, and to configure forward zones. It was discovered that the new netmask and IP addresses of forwarded zones were not sufficiently validated, allowing an authenticated user to inject new configuration directives into the Recursor's configuration.

## References
- http://www.securityfocus.com/bid/101982
- https://doc.powerdns.com/recursor/security-advisories/powerdns-advisory-2017-06.html
