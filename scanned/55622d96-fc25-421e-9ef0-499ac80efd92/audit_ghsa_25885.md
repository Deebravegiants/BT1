# [M]  Elasticsearch privilege escalation

## Summary
Severity: Medium
Advisory: GHSA-pgq6-ccqj-hpqr
CVE: CVE-2022-23708
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-pgq6-ccqj-hpqr
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.16.0 <7.17.1

## Details
A flaw was discovered in Elasticsearch 7.17.0’s upgrade assistant, in which upgrading from version 6.x to 7.x would disable the in-built protections on the security index, allowing authenticated users with “*” index permissions access to this index. Users running a cluster on an affected version that had previously been upgraded from 6.x, should upgrade to 7.17.1. Users that are planning to upgrade from 6.x should not perform an upgrade from 6.x to versions 7.16 through 7.17.0 and should use 7.17.1+ for upgrades from 6.x.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23708
- https://discuss.elastic.co/t/elastic-stack-7-17-1-security-update/298447
- https://security.netapp.com/advisory/ntap-20220729-0003
