# [M] Information disclosure in JBoss Weld

## Summary
Severity: Medium
Advisory: GHSA-338v-3958-8v8r
CVE: CVE-2014-8122
CWE: CWE-362
Ecosystem: Maven
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-338v-3958-8v8r
Type: github-advisory

## Affected
- Maven: `org.jboss.weld:weld-core-bom` — affected >=0 <2.2.8

## Details
Race condition in JBoss Weld before 2.2.8 and 3.x before 3.0.0 Alpha3 allows remote attackers to obtain information from a previous conversation via vectors related to a stale thread state.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8122
- https://github.com/weld/core/commit/29fd1107fd30579ad9bb23fae4dc3ba464205745
- https://github.com/weld/core/commit/6808b11cd6d97c71a2eed754ed4f955acd789086
- https://github.com/weld/core/commit/8e413202fa1af08c09c580f444e4fd16874f9c65
- https://exchange.xforce.ibmcloud.com/vulnerabilities/100892
- https://github.com/victims/victims-cve-db/blob/master/database/java/2014/8122.yaml
- https://github.com/weld/core
- http://rhn.redhat.com/errata/RHSA-2015-0215.html
- http://rhn.redhat.com/errata/RHSA-2015-0216.html
- http://rhn.redhat.com/errata/RHSA-2015-0217.html
- http://rhn.redhat.com/errata/RHSA-2015-0218.html
- http://rhn.redhat.com/errata/RHSA-2015-0675.html
- http://rhn.redhat.com/errata/RHSA-2015-0773.html
- http://rhn.redhat.com/errata/RHSA-2015-0850.html
- http://rhn.redhat.com/errata/RHSA-2015-0851.html
- http://rhn.redhat.com/errata/RHSA-2015-0920.html
- http://www.securityfocus.com/bid/74252
- http://www.securitytracker.com/id/1031741
