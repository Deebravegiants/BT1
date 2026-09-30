# [H] Keycloak vulnerable to uncontrolled resource consumption

## Summary
Severity: High
Advisory: GHSA-r32r-3977-cgc3
CVE: CVE-2014-3651
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-r32r-3977-cgc3
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <1.0.3

## Details
JBoss KeyCloak versions prior to 1.0.3.Final allow remote attackers to create a denial of service (resource consumption) by supplying a large value in the size parameter to auth/qrcode, related to QR code generation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3651
- https://bugzilla.redhat.com/show_bug.cgi?id=1144278
- https://github.com/advisories/GHSA-r32r-3977-cgc3
- https://issues.jboss.org/browse/KEYCLOAK-699
