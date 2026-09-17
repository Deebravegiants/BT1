# [M] Missing Authorization in Kibana Leading to Unauthorized Modification of Machine Learning Trained Model Space Assignments

## Summary
Severity: Medium
Advisory: BIT-elk-2026-72671
Aliases: BIT-kibana-2026-72671, CVE-2026-72671
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72671
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.4.5

## Details
A Kibana Machine Learning capability that removes a saved object from the current space accepts machine learning trained models as a target, but it verifies only the privileges that apply to anomaly detection jobs and data frame analytics jobs. A user whose role grants create anomaly detection jobs and data frame analytics jobs without the trained model privilege can therefore remove a trained model from a space. The model itself is not deleted and remains available in its other spaces, and the change can be reversed by a suitably privileged user.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-and-9-4-5-security-update-esa-2026-88/389525
- https://nvd.nist.gov/vuln/detail/CVE-2026-72671
