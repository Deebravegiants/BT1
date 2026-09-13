# [H] OpenSearch is vulnerable to DoS via complex query_string inputs

## Summary
Severity: High
Advisory: GHSA-mw3v-mmfw-3x2g
CVE: CVE-2025-9624
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-mw3v-mmfw-3x2g
Type: github-advisory

## Affected
- Maven: `org.opensearch:opensearch-common` — affected >=3.0.0 <3.3.0
- Maven: `org.opensearch:opensearch-common` — affected >=0 <2.19.4

## Details
A vulnerability in OpenSearch allows attackers to cause Denial of Service (DoS) by submitting complex query_string inputs.

This issue affects all OpenSearch versions below 2.19.4 and versions 3.0.0 through 3.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9624
- https://github.com/opensearch-project/OpenSearch/pull/19491
- https://caverav.cl/posts/opensearch-dos/opensearch-dos
- https://fluidattacks.com/advisories/chick
- https://github.com/opensearch-project/OpenSearch
- https://github.com/opensearch-project/OpenSearch/releases/tag/2.19.4
- https://github.com/opensearch-project/OpenSearch/releases/tag/3.3.0
- https://opensearch.org/blog/explore-opensearch-3-3
