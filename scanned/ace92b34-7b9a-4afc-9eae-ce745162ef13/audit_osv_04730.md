# [H] Incorrect Authorization in Kibana Leading to Disclosure of Elastic Defend Endpoint Event Data

## Summary
Severity: High
Advisory: BIT-elk-2026-72672
Aliases: BIT-kibana-2026-72672, CVE-2026-72672
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72672
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.1.0 <9.4.5

## Details
The Elastic Security capability that suggests existing field values while a user authors endpoint policy artifacts queries Elastic Defend event data with Kibana's internal Elasticsearch account instead of the account of the requesting user. Only Kibana feature privileges are verified, and the caller's Elasticsearch index privileges are not. An authenticated user who holds Elastic Security feature privileges but no read access to the Elastic Defend event indices can therefore retrieve field values from that data, including process command line arguments, which commonly contain tokens, credentials, connection strings, and other sensitive operational detail from protected hosts.

## References
- https://discuss.elastic.co/t/kibana-9-4-5-security-update-esa-2026-89/389536
- https://nvd.nist.gov/vuln/detail/CVE-2026-72672
