# [H] Asset Pipeline plugin for Grails vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-g7wm-22m6-5774
CVE: CVE-2018-17605
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g7wm-22m6-5774
Type: github-advisory

## Affected
- Maven: `org.grails.plugins:asset-pipeline` — affected >=0 <3.0.4

## Details
An issue was discovered in the Asset Pipeline plugin before 3.0.4 for Grails. An attacker can perform directory traversal via a crafted request when a servlet-based application is executed in Jetty, because there is a classloader vulnerability that can allow a reverse file traversal route in AssetPipelineFilter.groovy or AssetPipelineFilterCore.groovy.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17605
- https://github.com/grails/grails-core/issues/11068
- https://github.com/bertramdev/asset-pipeline/commit/a29533c52e4b60e244082433e116d2a038d01017
