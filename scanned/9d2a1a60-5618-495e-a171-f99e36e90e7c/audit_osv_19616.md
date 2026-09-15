# [C] CVE-2021-22910

## Summary
Severity: Critical
Advisory: CVE-2021-22910
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-09
Source: https://osv.dev/vulnerability/CVE-2021-22910
Type: osv

## Details
A sanitization vulnerability exists in Rocket.Chat server versions <3.13.2, <3.12.4, <3.11.4 that allowed queries to an endpoint which could result in a NoSQL injection, potentially leading to RCE.

## References
- https://blog.sonarsource.com/nosql-injections-in-rocket-chat/
- https://hackerone.com/reports/1130874
