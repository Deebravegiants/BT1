# [H] Allocation of resources without limits or throttling in keycloak-model-infinispan

## Summary
Severity: High
Advisory: GHSA-2vp8-jv5v-6qh6
CVE: CVE-2021-3637
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-07-13
Source: https://github.com/advisories/GHSA-2vp8-jv5v-6qh6
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-model-infinispan` — affected >=0 <14.0.0

## Details
A flaw was found in keycloak-model-infinispan in keycloak versions before 14.0.0 where authenticationSessions map in RootAuthenticationSessionEntity grows boundlessly which could lead to a DoS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3637
- https://bugzilla.redhat.com/show_bug.cgi?id=1979638
