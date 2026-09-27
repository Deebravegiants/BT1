# [M] RabbitMQ Node can log Basic Auth header from an HTTP request

## Summary
Severity: Medium
Advisory: BIT-rabbitmq-2025-50200
Aliases: CVE-2025-50200, GHSA-gh3x-4x42-fvq8
Ecosystem: Bitnami
Published: 2025-06-24
Source: https://osv.dev/vulnerability/BIT-rabbitmq-2025-50200
Type: osv

## Affected
- Bitnami: `rabbitmq` — affected >=0 <4.0.8

## Details
RabbitMQ is a messaging and streaming broker. In versions 3.13.7 and prior, RabbitMQ is logging authorization headers in plaintext encoded in base64. When querying RabbitMQ api with HTTP/s with basic authentication it creates logs with all headers in request, including authorization headers which show base64 encoded username:password. This is easy to decode and afterwards could be used to obtain control to the system depending on credentials. This issue has been patched in version 4.0.8.

## References
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-gh3x-4x42-fvq8
- https://nvd.nist.gov/vuln/detail/CVE-2025-50200
