# [H] Keycloak Unauthenticated Access

## Summary
Severity: High
Advisory: GHSA-8prc-58j4-m55q
CVE: CVE-2019-14832
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8prc-58j4-m55q
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-model-infinispan` — affected >=0 <7.0.1
- Maven: `org.keycloak:keycloak-model-jpa` — affected >=0 <7.0.1

## Details
A flaw was found in the Keycloak REST API before version 8.0.0, implemented in Keycloak before 7.0.1 where it would permit user access from a realm the user was not configured. An authenticated attacker with knowledge of a user id could use this flaw to access unauthorized information or to carry out further attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14832
- https://github.com/keycloak/keycloak/commit/0b73685ccf3181115ae3936a578708630215ac23
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14832
