# [M] Logstash Improper Certificate Validation in TCP output

## Summary
Severity: Medium
Advisory: BIT-logstash-2025-37730
Aliases: CVE-2025-37730
Ecosystem: Bitnami
Published: 2025-05-08
Source: https://osv.dev/vulnerability/BIT-logstash-2025-37730
Type: osv

## Affected
- Bitnami: `logstash` — affected >=9.0.0 <9.0.1

## Details
Improper certificate validation in Logstash's TCP output could lead to a man-in-the-middle (MitM) attack in “client” mode, as hostname verification in TCP output was not being performed when the ssl_verification_mode => full was set.

## References
- https://discuss.elastic.co/t/logstash-8-17-6-8-18-1-and-9-0-1-security-update-esa-2025-08/377869
- https://nvd.nist.gov/vuln/detail/CVE-2025-37730
