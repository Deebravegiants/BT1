# [C] Gluu Oxauth before v4.4.1 vulnerable to Server-Side Request Forgery attacks via a crafted request_uri parameter

## Summary
Severity: Critical
Advisory: GHSA-hc94-9v26-gxwv
CVE: CVE-2022-36663
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-07
Source: https://github.com/advisories/GHSA-hc94-9v26-gxwv
Type: github-advisory

## Affected
- Maven: `org.gluu:oxauth-common` — affected >=0 <4.4.1

## Details
Gluu Oxauth before v4.4.1 allows attackers to execute blind SSRF (Server-Side Request Forgery) attacks via a crafted request_uri parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36663
- https://github.com/GluuFederation/oxAuth/commit/58c4ac9bbf2addf4b419bf155de99db57a202f5c
- https://github.com/GluuFederation/oxAuth
- https://github.com/GluuFederation/oxAuth/releases/tag/4.4.1
- https://gluu.org/gluu-4-4-1
