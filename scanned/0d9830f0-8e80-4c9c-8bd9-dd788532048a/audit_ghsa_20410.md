# [M] Cross-site Scripting in Apache Pluto

## Summary
Severity: Medium
Advisory: GHSA-x588-g38j-f672
CVE: CVE-2021-36737
CWE: CWE-79
Ecosystem: Maven
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-x588-g38j-f672
Type: github-advisory

## Affected
- Maven: `org.apache.portals.pluto:pluto-portal` — affected >=0 <3.1.1

## Details
The input fields of the Apache Pluto UrlTestPortlet are vulnerable to Cross-Site Scripting (XSS) attacks. Users should migrate to version 3.1.1 of the v3-demo-portlet.war artifact

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36737
- https://github.com/apache/portals-pluto
- https://lists.apache.org/thread/x7kt47bf358x8sg9qg02zt0dmdrtow25
