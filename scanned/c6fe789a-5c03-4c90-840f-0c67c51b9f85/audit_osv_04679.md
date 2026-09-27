# [H] Missing Authorization in Elasticsearch Leading to Information Disclosure

## Summary
Severity: High
Advisory: BIT-elasticsearch-2026-78607
Aliases: CVE-2026-78607
Ecosystem: Bitnami
Published: 2026-09-03
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-78607
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.5.0 <9.5.1

## Details
Missing Authorization (CWE-862) in the Elasticsearch custom inference service can lead to information disclosure via Privilege Abuse (CAPEC-122). A user holding only inference execution privileges could cause outbound inference traffic to be directed to a destination of their choosing and could cause administrator-provisioned credentials to be exposed.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-19-9-3-8-9-4-4-9-5-1-security-update-esa-2026-143/390094
- https://nvd.nist.gov/vuln/detail/CVE-2026-78607
