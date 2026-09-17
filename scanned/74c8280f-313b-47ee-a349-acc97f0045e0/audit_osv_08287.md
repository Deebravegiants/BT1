# [M] CVE-2016-2120

## Summary
Severity: Medium
Advisory: CVE-2016-2120
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-01
Source: https://osv.dev/vulnerability/CVE-2016-2120
Type: osv

## Details
An issue has been found in PowerDNS Authoritative Server versions up to and including 3.4.10, 4.0.1 allowing an authorized user to crash the server by inserting a specially crafted record in a zone under their control then sending a DNS query for that record. The issue is due to an integer overflow when checking if the content of the record matches the expected size, allowing an attacker to cause a read past the buffer boundary.

## References
- https://www.debian.org/security/2017/dsa-3764
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-2120
