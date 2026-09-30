# [M] Jinjava calls getClass

## Summary
Severity: Medium
Advisory: GHSA-45r8-3495-x6rm
CVE: CVE-2018-18893
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-45r8-3495-x6rm
Type: github-advisory

## Affected
- Maven: `com.hubspot.jinjava:jinjava` — affected >=0 <2.4.6

## Details
Jinjava before 2.4.6 does not block the getClass method, related to com/hubspot/jinjava/el/ext/JinjavaBeanELResolver.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18893
- https://github.com/HubSpot/jinjava/pull/230
- https://github.com/HubSpot/jinjava
- https://github.com/HubSpot/jinjava/blob/master/CHANGES.md
- https://github.com/advisories/GHSA-45r8-3495-x6rm
