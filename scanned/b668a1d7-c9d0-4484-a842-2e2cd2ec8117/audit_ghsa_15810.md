# [M] Elasticsearch Insertion of Sensitive Information into Log File

## Summary
Severity: Medium
Advisory: GHSA-2hjr-vmf3-xwvp
CVE: CVE-2023-49921
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-26
Source: https://github.com/advisories/GHSA-2hjr-vmf3-xwvp
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=0 <7.17.16
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0 <8.11.2

## Details
An issue was discovered by Elastic whereby Watcher search input logged the search query results on DEBUG log level. This could lead to raw contents of documents stored in Elasticsearch to be printed in logs. Elastic has released 8.11.2 and 7.17.16 that resolves this issue by removing this excessive logging. This issue only affects users that use Watcher and have a Watch defined that uses the search input and additionally have set the search input’s logger to DEBUG or finer, for example using: org.elasticsearch.xpack.watcher.input.search, org.elasticsearch.xpack.watcher.input, org.elasticsearch.xpack.watcher, or wider, since the loggers are hierarchical.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49921
- https://discuss.elastic.co/t/elasticsearch-8-11-2-7-17-16-security-update-esa-2023-29/349179
- https://github.com/elastic/elasticsearch
