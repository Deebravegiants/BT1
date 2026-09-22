# [C] CVE-2017-2773

## Summary
Severity: Critical
Advisory: CVE-2017-2773
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-13
Source: https://osv.dev/vulnerability/CVE-2017-2773
Type: osv

## Details
An issue was discovered in Pivotal PCF Elastic Runtime 1.6.x versions prior to 1.6.60, 1.7.x versions prior to 1.7.41, 1.8.x versions prior to 1.8.23, and 1.9.x versions prior to 1.9.1. Incomplete validation logic in JSON Web Token (JWT) libraries can allow unprivileged attackers to impersonate other users in multiple components included in PCF Elastic Runtime, aka an "Unauthenticated JWT signing algorithm in multiple components" issue.

## References
- http://www.securityfocus.com/bid/97135
- https://pivotal.io/security/cve-2017-2773
