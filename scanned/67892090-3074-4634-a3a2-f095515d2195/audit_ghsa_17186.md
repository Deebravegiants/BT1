# [M] Elasticsearch Uncaught Exception leading to crash

## Summary
Severity: Medium
Advisory: GHSA-pw39-f3m5-cxfc
CVE: CVE-2024-23449
CWE: CWE-248
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-pw39-f3m5-cxfc
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.4.0 <8.11.1

## Details
An uncaught exception in Elasticsearch >= 8.4.0 and < 8.11.1 occurs when an encrypted PDF is passed to an attachment processor through the REST API. The Elasticsearch ingest node that attempts to parse the PDF file will crash. This does not happen with password-protected PDF files or with unencrypted PDF files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23449
- https://github.com/elastic/elasticsearch/commit/a59180459a3cb30b71399d778943cab4ac2191c4
- https://github.com/elastic/elasticsearch/commit/f9bf18a716613473fc1cb96c838874e1f9f6ba22
- https://discuss.elastic.co/t/elasticsearch-8-11-1-security-update-esa-2024-05/356458
- https://github.com/elastic/elasticsearch
