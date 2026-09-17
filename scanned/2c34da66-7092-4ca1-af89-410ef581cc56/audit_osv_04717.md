# [M] Incorrect Authorization in Kibana Leading to Machine Learning Audit Log Integrity Compromise

## Summary
Severity: Medium
Advisory: BIT-elk-2026-63145
Aliases: BIT-kibana-2026-63145, CVE-2026-63145
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-elk-2026-63145
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.4

## Details
Incorrect Authorization (CWE-863) in Kibana can lead to integrity compromise of Machine Learning audit and notification records via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1).

A vulnerability exists in Kibana's Machine Learning functionality where a Machine Learning management endpoint performs an insufficient authorization check. The endpoint validates only a coarse privilege level but does not verify that the requesting user has access to the specific Machine Learning job or notification resources provided in the request. As a result, a low-privileged user with Machine Learning access in any Kibana space can manipulate Machine Learning audit and notification records for arbitrary jobs—including jobs in other spaces or belonging to other users—by leveraging Kibana's internally elevated credentials to write to restricted Machine Learning system indices that the user cannot access directly.

## References
- https://discuss.elastic.co/t/kibana-8-19-19-9-3-8-9-4-4-security-update-esa-2026-69/388572
- https://nvd.nist.gov/vuln/detail/CVE-2026-63145
