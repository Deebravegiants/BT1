# [M] CVE-2018-11087

## Summary
Severity: Medium
Advisory: CVE-2018-11087
Aliases: GHSA-w4g2-9hj6-5472
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-14
Source: https://osv.dev/vulnerability/CVE-2018-11087
Type: osv

## Details
Pivotal Spring AMQP, 1.x versions prior to 1.7.10 and 2.x versions prior to 2.0.6, expose a man-in-the-middle vulnerability due to lack of hostname validation. A malicious user that has the ability to intercept traffic would be able to view data in transit.

## References
- https://pivotal.io/security/cve-2018-11087
