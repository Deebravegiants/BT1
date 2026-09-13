# [H] Elasticsearch privilege escalation

## Summary
Severity: High
Advisory: BIT-elasticsearch-2021-37937
Aliases: CVE-2021-37937
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2021-37937
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=7.13.0 <7.14.1

## Details
An issue was found with how API keys are created with the Fleet-Server service account. When an API key is created with a service account, it is possible that the API key could be created with higher privileges than intended. Using this vulnerability, a compromised Fleet-Server service account could escalate themselves to a super-user.

## References
- https://discuss.elastic.co/t/elastic-stack-7-14-1-security-update/283077
- https://www.elastic.co/community/security
- https://nvd.nist.gov/vuln/detail/CVE-2021-37937
