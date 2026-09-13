# [H] Observable Discrepancy in Kibana Fleet Leading to Disclosure of Elastic Agent Elasticsearch API Keys

## Summary
Severity: High
Advisory: BIT-elk-2026-72632
Aliases: BIT-kibana-2026-72632, CVE-2026-72632
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72632
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.1

## Details
Observable Discrepancy (CWE-203) in Kibana Fleet can lead to information disclosure via Excavation (CAPEC-116). Fleet removes the Elasticsearch API key value of an enrolled Elastic Agent from the responses of its agent listing capability, but that capability accepted caller-supplied filter expressions over the stored field that holds the value, and evaluated them with Kibana's own internal Elasticsearch privileges rather than the caller's. Because the number of matching agents is reported back to the caller, the difference between a matching and a non-matching filter formed a side channel from which the full API key value could be reconstructed one character at a time with a short sequence of requests.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-9-4-5-9-5-1-security-update-esa-2026-129/389532
- https://nvd.nist.gov/vuln/detail/CVE-2026-72632
