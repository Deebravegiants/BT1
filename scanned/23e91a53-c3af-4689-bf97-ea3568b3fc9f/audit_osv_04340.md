# [C] RCE via malicious SNS subscription payload

## Summary
Severity: Critical
Advisory: BIT-discourse-2021-41163
Aliases: CVE-2021-41163, GHSA-jcjx-pvpc-qgwq
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-41163
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.9

## Details
Discourse is an open source platform for community discussion. In affected versions maliciously crafted requests could lead to remote code execution. This resulted from a lack of validation in subscribe_url values. This issue is patched in the latest stable, beta and tests-passed versions of Discourse. To workaround the issue without updating, requests with a path starting /webhooks/aws path could be blocked at an upstream proxy.

## References
- https://github.com/discourse/discourse/commit/fa3c46cf079d28b086fe1025349bb00223a5d5e9
- https://github.com/discourse/discourse/security/advisories/GHSA-jcjx-pvpc-qgwq
- https://nvd.nist.gov/vuln/detail/CVE-2021-41163
