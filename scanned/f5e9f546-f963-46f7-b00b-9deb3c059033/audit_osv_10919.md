# [H] CVE-2017-4966

## Summary
Severity: High
Advisory: CVE-2017-4966
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-13
Source: https://osv.dev/vulnerability/CVE-2017-4966
Type: osv

## Details
An issue was discovered in these Pivotal RabbitMQ versions: all 3.4.x versions, all 3.5.x versions, and 3.6.x versions prior to 3.6.9; and these RabbitMQ for PCF versions: all 1.5.x versions, 1.6.x versions prior to 1.6.18, and 1.7.x versions prior to 1.7.15. RabbitMQ management UI stores signed-in user credentials in a browser's local storage without expiration, making it possible to retrieve them using a chained attack.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00011.html
- https://pivotal.io/security/cve-2017-4966
