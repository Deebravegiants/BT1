# [M] Stored Cross Site Scripting in Grails Fields Plugin

## Summary
Severity: Medium
Advisory: GHSA-q25j-gcmv-5qpp
CVE: CVE-2018-1000529
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-q25j-gcmv-5qpp
Type: github-advisory

## Affected
- Maven: `org.grails.plugins:fields` — affected >=0 <2.2.8
- Maven: `org.grails:grails-core` — affected >=0 <3.3.6

## Details
Grails Fields plugin version 2.2.7 contains a Cross Site Scripting (XSS) vulnerability in using the display tag that can result in XSS. This vulnerability has been fixed in version 2.2.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000529
- https://github.com/grails-fields-plugin/grails-fields/issues/278
- https://github.com/advisories/GHSA-q25j-gcmv-5qpp
- https://github.com/grails-fields-plugin/grails-fields
- https://github.com/martinfrancois/CVE-2018-1000529
