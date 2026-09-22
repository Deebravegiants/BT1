# [M] Eucalyptus Unauthorized Access to CC/NC Log Files

## Summary
Severity: Medium
Advisory: GHSA-f5hm-h272-2qwm
CVE: CVE-2013-4766
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f5hm-h272-2qwm
Type: github-advisory

## Affected
- Maven: `org.jclouds.api:eucalyptus` — affected >=0 <3.3.1

## Details
The gather log service in Eucalyptus before 3.3.1 allows remote attackers to read log files via an unspecified request to the (1) Cluster Controller (CC) or (2) Node Controller (NC) component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4766
- https://github.com/eucalyptus/eucalyptus
- http://www.eucalyptus.com/resources/security/advisories/esa-13
