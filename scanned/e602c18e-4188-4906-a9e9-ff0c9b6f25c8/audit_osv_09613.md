# [M] CVE-2017-1000395

## Summary
Severity: Medium
Advisory: CVE-2017-1000395
Aliases: GHSA-wqv4-9gr3-3qgh
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2017-1000395
Type: osv

## Details
Jenkins 2.73.1 and earlier, 2.83 and earlier provides information about Jenkins user accounts which is generally available to anyone with Overall/Read permissions via the /user/(username)/api remote API. This included e.g. Jenkins users' email addresses if the Mailer Plugin is installed. The remote API now no longer includes information beyond the most basic (user ID and name) unless the user requesting it is a Jenkins administrator.

## References
- https://jenkins.io/security/advisory/2017-10-11/
