# [M] Moderate severity vulnerability that affects org.apache.oozie:oozie-core

## Summary
Severity: Medium
Advisory: GHSA-wg5w-vv93-3f7w
CVE: CVE-2018-11799
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-wg5w-vv93-3f7w
Type: github-advisory

## Affected
- Maven: `org.apache.oozie:oozie-core` — affected >=0 <5.1.0

## Details
Vulnerability allows a user of Apache Oozie 3.1.3-incubating to 5.0.0 to impersonate other users. The malicious user can construct an XML that results workflows running in other user's name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11799
- https://github.com/advisories/GHSA-wg5w-vv93-3f7w
- https://lists.apache.org/thread.html/347e7a8cb86014b7ca37e49eb00b8d088203bdc0bcfb4799f8e5955a@%3Cuser.oozie.apache.org%3E
- http://www.securityfocus.com/bid/106266
