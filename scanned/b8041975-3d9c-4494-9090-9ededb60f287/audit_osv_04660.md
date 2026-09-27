# [M] BIT-elasticsearch-2020-7019

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2020-7019
Aliases: CVE-2020-7019, GHSA-c77j-p484-h84m
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2020-7019
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=7.0.0 <7.9.0

## Details
In Elasticsearch before 7.9.0 and 6.8.12 a field disclosure flaw was found when running a scrolling search with Field Level Security. If a user runs the same query another more privileged user recently ran, the scrolling search can leak fields that should be hidden. This could result in an attacker gaining additional permissions against a restricted index.

## References
- https://discuss.elastic.co/t/elastic-stack-7-9-0-and-6-8-12-security-update/245456
- https://security.netapp.com/advisory/ntap-20200827-0001/
- https://nvd.nist.gov/vuln/detail/CVE-2020-7019
