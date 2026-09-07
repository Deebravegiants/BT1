# [M] Concurrent Execution using Shared Resource with Improper Synchronization in Elasticsearch

## Summary
Severity: Medium
Advisory: GHSA-jqm6-m3j3-8gg9
CVE: CVE-2019-7614
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jqm6-m3j3-8gg9
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=0 <6.8.2
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0 <7.2.1

## Details
A race condition flaw was found in the response headers Elasticsearch versions before 7.2.1 and 6.8.2 returns to a request. On a system with multiple users submitting requests, it could be possible for an attacker to gain access to response header containing sensitive data from another user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7614
- https://github.com/elastic/elasticsearch
- https://www.elastic.co/community/security
