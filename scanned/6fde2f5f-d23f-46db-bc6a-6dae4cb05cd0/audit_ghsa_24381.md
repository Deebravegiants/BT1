# [H] Apache Ranger Access Restriction Bypass

## Summary
Severity: High
Advisory: GHSA-22v7-w6c5-v4rr
CVE: CVE-2016-0735
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-22v7-w6c5-v4rr
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0.5.0 <0.5.2

## Details
Apache Ranger 0.5.x before 0.5.2 allows remote authenticated users to bypass intended parent resource-level access restrictions by leveraging mishandling of a resource-level exclude policy.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0735
- https://github.com/apache/ranger/commit/18f216d0201eab93daea0b57035f7e6e3280bcfd
- https://github.com/apache/ranger
- http://mail-archives.apache.org/mod_mbox/ranger-dev/201603.mbox/%3CD31EE434.14B879%25vel%40apache.org%3E
