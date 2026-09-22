# [C] RCE via Prototype Pollution in OpenSearch Dashboards

## Summary
Severity: Critical
Advisory: CVE-2026-18420
Aliases: GHSA-xmqx-xq2p-8jq2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-18420
Type: osv

## Details
Improper input validation in the Time Series Visual Builder (TSVB) plugin in OpenSearch Dashboards allows an authenticated remote user to execute arbitrary code on the server via a crafted JSON payload to the metrics visualization API endpoint. This issue is a form of prototype pollution that enables remote code execution. 



To remediate this issue, users should upgrade to OpenSearch Dashboards 3.8 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-085-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18420.json
- https://github.com/opensearch-project/OpenSearch-Dashboards/security/advisories/GHSA-xmqx-xq2p-8jq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-18420
- https://github.com/opensearch-project/OpenSearch-Dashboards/releases/tag/3.8.0
