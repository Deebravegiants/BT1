# [C] CVE-2017-6080

## Summary
Severity: Critical
Advisory: CVE-2017-6080
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-13
Source: https://osv.dev/vulnerability/CVE-2017-6080
Type: osv

## Details
An issue was discovered in Zammad before 1.0.4, 1.1.x before 1.1.3, and 1.2.x before 1.2.1, caused by lack of a protection mechanism involving HTTP Access-Control headers. To exploit the vulnerability, an attacker can send cross-domain requests directly to the REST API for users with a valid session cookie and receive the result.

## References
- http://www.securityfocus.com/bid/96937
- https://zammad.com/de/news/security-advisory-zaa-2017-01
