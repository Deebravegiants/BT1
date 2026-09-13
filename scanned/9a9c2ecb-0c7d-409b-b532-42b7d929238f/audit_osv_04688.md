# [C] BIT-elk-2024-37288

## Summary
Severity: Critical
Advisory: BIT-elk-2024-37288
Aliases: BIT-kibana-2024-37288, CVE-2024-37288
Ecosystem: Bitnami
Published: 2024-09-11
Source: https://osv.dev/vulnerability/BIT-elk-2024-37288
Type: osv

## Affected
- Bitnami: `elk` — affected >=8.15.0 <8.15.1

## Details
A deserialization issue in Kibana can lead to arbitrary code execution when Kibana attempts to parse a YAML document containing a crafted payload. This issue only affects users that use  Elastic Security’s built-in AI tools https://www.elastic.co/guide/en/security/current/ai-for-security.html  and have configured an  Amazon Bedrock connector https://www.elastic.co/guide/en/security/current/assistant-connect-to-bedrock.html .

## References
- https://discuss.elastic.co/t/kibana-8-15-1-security-update-esa-2024-27-esa-2024-28/366119
- https://nvd.nist.gov/vuln/detail/CVE-2024-37288
