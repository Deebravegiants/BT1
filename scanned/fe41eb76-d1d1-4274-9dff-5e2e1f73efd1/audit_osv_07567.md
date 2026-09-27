# [M] Apache Superset: Possible SSRF on import datasets

## Summary
Severity: Medium
Advisory: BIT-superset-2023-25504
Aliases: CVE-2023-25504, GHSA-fxjg-28fm-pfxh, PYSEC-2026-1179
Ecosystem: Bitnami
Published: 2025-02-05
Source: https://osv.dev/vulnerability/BIT-superset-2023-25504
Type: osv

## Affected
- Bitnami: `superset` — affected >=0 <2.0.2

## Details
A malicious actor who has been authenticated and granted specific permissions in Apache Superset may use the import dataset feature in order to conduct Server-Side Request Forgery
attacks and query internal resources on behalf of the server where Superset
is deployed. This vulnerability exists in Apache Superset versions up to and including 2.0.1.

## References
- http://www.openwall.com/lists/oss-security/2023/04/18/8
- https://lists.apache.org/thread/tdnzkocfsqg2sbbornnp9g492fn4zhtx
- https://nvd.nist.gov/vuln/detail/CVE-2023-25504
