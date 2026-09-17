# [M] Argument Injection in Apache Geode server

## Summary
Severity: Medium
Advisory: GHSA-p426-qw2p-v95v
CVE: CVE-2017-15694
CWE: CWE-88
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-06-26
Source: https://github.com/advisories/GHSA-p426-qw2p-v95v
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=0 <1.9.0

## Details
When an Apache Geode server versions 1.0.0 to 1.8.0 is operating in secure mode, a user with write permissions for specific data regions can modify internal cluster metadata. A malicious user could modify this data in a way that affects the operation of the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15694
- https://lists.apache.org/thread.html/311505e7b7a045aaa246f0a1935703acacf41b954621b1363c40bf6f@%3Cuser.geode.apache.org%3E
