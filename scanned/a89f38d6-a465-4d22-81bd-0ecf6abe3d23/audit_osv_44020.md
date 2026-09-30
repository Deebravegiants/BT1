# [C] Code Injection via Gremlin Query Passthrough in Amazon Athena Neptune Connector

## Summary
Severity: Critical
Advisory: CVE-2026-77810
Aliases: GHSA-v7c2-5wfg-qg44
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77810
Type: osv

## Details
In the Neptune connector, a user with access to Neptune through Athena Federated Query could gain access to properties in the Lambda supplying the compute for the connector. To remediate this issue, users should upgrade to aws-athena-query-federation v2026.30.1 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-087-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77810.json
- https://github.com/awslabs/aws-athena-query-federation/security/advisories/GHSA-v7c2-5wfg-qg44
- https://nvd.nist.gov/vuln/detail/CVE-2026-77810
- https://github.com/awslabs/aws-athena-query-federation/releases/tag/v2026.30.1
