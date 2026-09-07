# [C] keycloak Self Stored Cross-site Scripting vulnerability

## Summary
Severity: Critical
Advisory: GHSA-q6w2-89hq-hq27
CVE: CVE-2021-20195
CWE: CWE-116, CWE-20, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-q6w2-89hq-hq27
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <13.0.0

## Details
A flaw was found in keycloak in versions before 13.0.0. A Self Stored XSS attack vector escalating to a complete account takeover is possible due to user-supplied data fields not being properly encoded and Javascript code being used to process the data. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20195
- https://github.com/keycloak/keycloak/commit/717d9515fa131e3d8c8936e41b2e52270fdec976
- https://bugzilla.redhat.com/show_bug.cgi?id=1919143
