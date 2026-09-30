# [H] Apache Geode information disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-2gw6-73wc-x88f
CVE: CVE-2017-5649
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2gw6-73wc-x88f
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.1.0 <1.1.1

## Details
Apache Geode before 1.1.1, when a cluster has enabled security by setting the security-manager property, allows remote authenticated users with CLUSTER:READ but not DATA:READ permission to access the data browser page in Pulse and consequently execute an OQL query that exposes data stored in the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5649
- http://mail-archives.apache.org/mod_mbox/geode-user/201704.mbox/%3cCAEwge-E4y=EVfhwpfRwsbnBH_hBS3Q-BJS+1BX5omYGW4dnR1w@mail.gmail.com%3e
