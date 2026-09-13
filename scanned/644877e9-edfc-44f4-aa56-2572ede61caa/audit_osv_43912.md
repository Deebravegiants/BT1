# [M] Incorrect privilege assignment in the Amazon aws-athena-query-federation ClickHouse connector deployment template

## Summary
Severity: Medium
Advisory: CVE-2026-75910
Aliases: GHSA-vmjg-c6wv-wjm9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-75910
Type: osv

## Details
Incorrect privilege assignment in the ClickHouse connector deployment template in Amazon Athena Federated Query prior to v2026.17.1 could allow an authenticated remote user to read arbitrary AWS Secrets Manager secrets in the deploying account by pointing the connector's connection string at an unrelated secret and at a database endpoint under the user's control, causing the connector to transmit the secret to that endpoint. To remediate this issue, users should upgrade to aws-athena-query-federation connectors version v2026.17.1 or later and ensure that any forked or derivative code is patched to incorporate the new fixes. Alternatively, to remediate this issue, users should redeploy the connector with the current template and supply a non-empty SecretNamePrefix value.

## References
- https://aws.amazon.com/security/security-bulletins/2026-084-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75910.json
- https://github.com/awslabs/aws-athena-query-federation/security/advisories/GHSA-vmjg-c6wv-wjm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-75910
- https://github.com/awslabs/aws-athena-query-federation/releases/tag/v2026.17.1
