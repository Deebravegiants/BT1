# [C] CVE-2016-9877

## Summary
Severity: Critical
Advisory: CVE-2016-9877
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-9877
Type: osv

## Details
An issue was discovered in Pivotal RabbitMQ 3.x before 3.5.8 and 3.6.x before 3.6.6 and RabbitMQ for PCF 1.5.x before 1.5.20, 1.6.x before 1.6.12, and 1.7.x before 1.7.7. MQTT (MQ Telemetry Transport) connection authentication with a username/password pair succeeds if an existing username is provided but the password is omitted from the connection request. Connections that use TLS with a client-provided certificate are not affected.

## References
- http://www.securityfocus.com/bid/95065
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbst03880en_us
- http://www.debian.org/security/2017/dsa-3761
- https://pivotal.io/security/cve-2016-9877
