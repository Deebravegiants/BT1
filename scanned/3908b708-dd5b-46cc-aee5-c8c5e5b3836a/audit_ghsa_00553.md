# [M] Improper Control of Interaction Frequency in Apache syncope-core

## Summary
Severity: Medium
Advisory: GHSA-9h9c-f287-c6vp
CVE: CVE-2018-17184
CWE: CWE-799
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-9h9c-f287-c6vp
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope-core` — affected >=0 <2.0.11
- Maven: `org.apache.syncope:syncope-core` — affected >=2.1.0 <2.1.2

## Details
A malicious user with enough administration entitlements can inject html-like elements containing JavaScript statements into Connector names, Report names, AnyTypeClass keys and Policy descriptions. When another user with enough administration entitlements edits one of the Entities above via Admin Console, the injected JavaScript code is executed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17184
- https://github.com/advisories/GHSA-9h9c-f287-c6vp
- https://syncope.apache.org/security#CVE-2018-17184:_Stored_XSS
