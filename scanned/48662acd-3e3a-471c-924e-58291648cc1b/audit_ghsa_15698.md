# [M] Elasticsearch stores private key on disk unencrypted

## Summary
Severity: Medium
Advisory: GHSA-5v8f-xx9m-wj44
CVE: CVE-2024-23444
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-5v8f-xx9m-wj44
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0-alpha1 <8.13.0
- Maven: `org.elasticsearch:elasticsearch` — affected >=0 <7.17.23

## Details
It was discovered by Elastic engineering that when elasticsearch-certutil CLI tool is used with the csr option in order to create a new Certificate Signing Requests, the associated private key that is generated is stored on disk unencrypted even if the `--pass` parameter is passed in the command invocation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23444
- https://github.com/elastic/elasticsearch/pull/106105
- https://github.com/elastic/elasticsearch/pull/109834
- https://github.com/elastic/elasticsearch/commit/07296d596a1dee24730e33ad40b6726f70c6fc23
- https://github.com/elastic/elasticsearch/commit/321c4e1e6b738bf80faa41dbb9881489a4ab44e5
- https://github.com/elastic/elasticsearch/commit/bb1eddada3678257838b0590090ff9eb68acaa1b
- https://discuss.elastic.co/t/elasticsearch-8-13-0-7-17-23-security-update-esa-2024-12/364157
- https://github.com/elastic/elasticsearch
- https://security.netapp.com/advisory/ntap-20250404-0001
