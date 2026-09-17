# [M] Arbitrary file read in rabbitmq-aws plugin

## Summary
Severity: Medium
Advisory: CVE-2026-9133
Aliases: GHSA-8554-wg4r-7hxm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-9133
Type: osv

## Details
Active debug code exists in the ARN resolver of amazon-mq rabbitmq-aws before version 0.2.1. A debug ARN scheme (arn:aws-debug:file) accepted by the PUT /api/aws/arn/validate validation endpoint might allow remote authenticated users to perform arbitrary file reads on any file accessible to the RabbitMQ process. 



To remediate this issue, customers should upgrade to version 0.2.1 of rabbitmq-aws. If RabbitMQ is configured to use TLS for connections, we also recommend rotating any associated private certificate keys.

## References
- https://aws.amazon.com/security/security-bulletins/2026-034-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9133.json
- https://github.com/amazon-mq/rabbitmq-aws/security/advisories/GHSA-8554-wg4r-7hxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-9133
- https://github.com/amazon-mq/rabbitmq-aws/releases/tag/0.2.1
