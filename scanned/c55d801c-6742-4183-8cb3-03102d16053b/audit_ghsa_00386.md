# [M] Path Traversal in org.springframework:spring-core

## Summary
Severity: Medium
Advisory: GHSA-g8hw-794c-4j9g
CVE: CVE-2018-1271
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-g8hw-794c-4j9g
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=5.0.0 <5.0.5
- Maven: `org.springframework:spring-core` — affected >=0 <4.3.15

## Details
Spring Framework, versions 5.0 prior to 5.0.5 and versions 4.3 prior to 4.3.15 and older unsupported versions, allow applications to configure Spring MVC to serve static resources (e.g. CSS, JS, images). When static resources are served from a file system on Windows (as opposed to the classpath, or the ServletContext), a malicious user can send a request using a specially crafted URL that can lead a directory traversal attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1271
- https://github.com/spring-projects/spring-framework/commit/0e28bee0f155b9bf240b4bafc4646e4810cb23f8
- https://github.com/spring-projects/spring-framework/commit/13356a7ee2240f740737c5c83bdccdacc30603ab
- https://github.com/spring-projects/spring-framework/commit/695bf2961feffd35b5560ccc982a2189dcca611f
- https://github.com/spring-projects/spring-framework/commit/91b803a2310344d925e5d4b1709bbcea90375548
- https://github.com/spring-projects/spring-framework/commit/98ad23bef8e2e04143f8f5b201380543a8d8c0c3
- https://github.com/spring-projects/spring-framework/commit/b9ebdaaf3710db473a2e1fec8641c316483a22aa
- https://github.com/spring-projects/spring-framework/commit/f046a066eceefa0799d1bc89bd6e1318f39bdf69
- https://github.com/spring-projects/spring-framework/commit/f59ea610dfcf55cd0b42f6dd76a9b3dab0218aaa
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://pivotal.io/security/cve-2018-1271
- https://github.com/advisories/GHSA-g8hw-794c-4j9g
- https://access.redhat.com/errata/RHSA-2018:2939
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:1320
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
