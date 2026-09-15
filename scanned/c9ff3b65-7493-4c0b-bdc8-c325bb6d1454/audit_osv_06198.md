# [H] Missing Authorization in Kibana Machine Learning Leading to Cross-Space Information Disclosure and Unauthorized Data Modification

## Summary
Severity: High
Advisory: BIT-kibana-2026-72675
Aliases: BIT-elk-2026-72675, CVE-2026-72675
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-kibana-2026-72675
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.0.0 <9.4.5

## Details
Missing Authorization (CWE-862) in Kibana can lead to cross-space information disclosure and unauthorized data modification via Privilege Abuse (CAPEC-122). Kibana Machine Learning carries out its Elasticsearch operations with elevated internal permissions and relies on a per-request space filter to keep the machine learning data of one space separated from another. Part of the Machine Learning functionality did not apply that filter, so operations issued from one space were carried out against the machine learning data of every space in the deployment.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-and-9-4-5-security-update-esa-2026-92/389526
- https://nvd.nist.gov/vuln/detail/CVE-2026-72675
