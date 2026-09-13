# [H] Authorization Bypass Through User-Controlled Key in Kibana Leading to Cross-Space Access to Machine Learning Trained Models

## Summary
Severity: High
Advisory: BIT-elk-2026-72629
Aliases: BIT-kibana-2026-72629, CVE-2026-72629
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72629
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.1

## Details
Authorization Bypass Through User-Controlled Key (CWE-639) in Kibana can lead to unauthorized cross-space access via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). The result is disclosure of inference output from a trained model in a different space that the user is not authorized to list, read, or use, which exposes the behavior of a model. The same pattern also reached the deployment stop and deployment update operations, allowing an active trained model deployment in another space to be stopped or to have its allocated resources altered.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-9-4-5-9-5-1-security-update-esa-2026-126/389530
- https://nvd.nist.gov/vuln/detail/CVE-2026-72629
