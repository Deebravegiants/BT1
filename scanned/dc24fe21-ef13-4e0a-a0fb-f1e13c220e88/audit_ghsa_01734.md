# [M] Improper Restriction of Rendered UI Layers or Frames in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-3gg7-9q2x-79fc
CVE: CVE-2020-1728
CWE: CWE-1021
Ecosystem: Maven
Published: 2020-04-15
Source: https://github.com/advisories/GHSA-3gg7-9q2x-79fc
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0

## Details
A vulnerability was found in all versions of Keycloak where, the pages on the Admin Console area of the application are completely missing general HTTP security headers in HTTP-responses. This does not directly lead to a security issue, yet it might aid attackers in their efforts to exploit other problems. The flaws unnecessarily make the servers more prone to Clickjacking, channel downgrade attacks and other similar client-based attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1728
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1728
- https://issues.redhat.com/browse/KEYCLOAK-12264
