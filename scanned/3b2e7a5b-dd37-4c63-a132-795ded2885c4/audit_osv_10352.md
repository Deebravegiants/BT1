# [M] CVE-2017-15090

## Summary
Severity: Medium
Advisory: CVE-2017-15090
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2017-15090
Type: osv

## Details
An issue has been found in the DNSSEC validation component of PowerDNS Recursor from 4.0.0 and up to and including 4.0.6, where the signatures might have been accepted as valid even if the signed data was not in bailiwick of the DNSKEY used to sign it. This allows an attacker in position of man-in-the-middle to alter the content of records by issuing a valid signature for the crafted records.

## References
- http://www.securityfocus.com/bid/101982
- https://doc.powerdns.com/recursor/security-advisories/powerdns-advisory-2017-03.html
