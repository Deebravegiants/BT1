# [H] RabbitMQ MQTT Topic Permission Authorization Bypass

## Summary
Severity: High
Advisory: BIT-rabbitmq-2026-44838
Aliases: CVE-2026-44838, GHSA-x866-xp2g-cx8v
Ecosystem: Bitnami
Published: 2026-05-29
Source: https://osv.dev/vulnerability/BIT-rabbitmq-2026-44838
Type: osv

## Affected
- Bitnami: `rabbitmq` — affected >=4.2.0 <4.2.4

## Details
RabbitMQ is a messaging and streaming broker. From 4.2.0 to before 4.2.4, RabbitMQ's MQTT plugin allows for topic-level authorization using regular expressions with variable substitution. Administrators can create patterns such as ^{client_id}-sensors$ to restrict user access to topics that include their client ID. However, the client_id is provided by the user in the MQTT CONNECT packet and is inserted into the regex pattern without escaping special regex characters. This flaw enables an authenticated MQTT user to inject regex operators to bypass authorization. This vulnerability is fixed in 4.2.4 and 4.3.0.

## References
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-x866-xp2g-cx8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44838
