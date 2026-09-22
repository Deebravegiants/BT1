# [H] Keycloak code execution via UMA policy abuse

## Summary
Severity: High
Advisory: GHSA-9c24-43p5-fv82
CVE: CVE-2019-10169
CWE: CWE-267
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9c24-43p5-fv82
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-authz-client` — affected >=0 <8.0.0

## Details
A flaw was found in Keycloak’s user-managed access interface, where it would permit a script to be set in the UMA policy. This flaw allows an authenticated attacker with UMA permissions to configure a malicious script to trigger and execute arbitrary code with the permissions of the user running application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10169
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10169
- https://github.com/keycloak/keycloak
- https://security.snyk.io/vuln/SNYK-JAVA-ORGKEYCLOAK-568797
