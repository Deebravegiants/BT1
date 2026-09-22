# [M] Prototype Pollution in GraphHopper

## Summary
Severity: Medium
Advisory: GHSA-qhxh-9hhx-6p7v
CVE: CVE-2021-23408
CWE: CWE-1321
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-qhxh-9hhx-6p7v
Type: github-advisory

## Affected
- Maven: `com.graphhopper:graphhopper-web-bundle` — affected >=0 <3.2

## Details
This affects the package `com.graphhopper:graphhopper-web-bundle` before 3.2, from 4.0-pre1 and before 4.0. The URL parser could be tricked into adding or modifying properties of Object.prototype using a constructor or __proto__ payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23408
- https://github.com/graphhopper/graphhopper/pull/2370
- https://github.com/graphhopper/graphhopper/releases/tag/3.1
- https://github.com/graphhopper/graphhopper/releases/tag/3.2
- https://snyk.io/vuln/SNYK-JAVA-COMGRAPHHOPPER-1320114
