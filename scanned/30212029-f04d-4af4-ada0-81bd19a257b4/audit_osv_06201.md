# [H] Incorrect Authorization in Kibana Leading to Privilege Escalation

## Summary
Severity: High
Advisory: BIT-kibana-2026-78583
Aliases: BIT-elk-2026-78583, CVE-2026-78583
Ecosystem: Bitnami
Published: 2026-09-09
Source: https://osv.dev/vulnerability/BIT-kibana-2026-78583
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.5.0 <9.5.3

## Details
Incorrect Authorization (CWE-863) in Kibana can lead to privilege escalation via Input Data Manipulation (CAPEC-153). Elasticsearch cluster privilege declarations originating from integration packages were not validated before being used to mint credentials for enrolled Elastic Agents. A user holding Fleet management privileges could therefore cause every Elastic Agent on a targeted policy to receive a credential carrying arbitrarily elevated Elasticsearch cluster privileges, up to and including full cluster administration.

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-9-5-3-security-update-esa-2026-140/390158
- https://nvd.nist.gov/vuln/detail/CVE-2026-78583
