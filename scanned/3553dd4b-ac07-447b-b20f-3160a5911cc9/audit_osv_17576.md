# [M] CVE-2020-1722

## Summary
Severity: Medium
Advisory: CVE-2020-1722
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-04-27
Source: https://osv.dev/vulnerability/CVE-2020-1722
Type: osv

## Details
A flaw was found in all ipa versions 4.x.x through 4.8.0. When sending a very long password (>= 1,000,000 characters) to the server, the password hashing process could exhaust memory and CPU leading to a denial of service and the website becoming unresponsive. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1722
