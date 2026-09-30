# [H] Missing Input Validation in Threat Intel Feed Parser in OpenSearch Security Analytics Plugin

## Summary
Severity: High
Advisory: CVE-2026-18952
Aliases: GHSA-w946-8jxc-6v3m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-18952
Type: osv

## Details
Missing input validation in the threat intelligence feed parser in the OpenSearch Security Analytics plugin might allow an authenticated remote user to perform server-side request forgery and read local files via a crafted URL parameter to the threat intel source configuration endpoint.

## References
- https://aws.amazon.com/security/security-bulletins/2026-079-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18952.json
- https://github.com/opensearch-project/security-analytics/security/advisories/GHSA-w946-8jxc-6v3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-18952
- https://docs.aws.amazon.com/opensearch-service/latest/developerguide/service-software.html
