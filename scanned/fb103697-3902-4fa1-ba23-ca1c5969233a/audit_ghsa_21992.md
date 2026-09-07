# [M] Incorrect Permission Assignment for Critical Resource and Permissive List of Allowed Inputs in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-72j4-94rx-cr6w
CVE: CVE-2020-1694
CWE: CWE-183, CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-72j4-94rx-cr6w
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <10.0.0

## Details
A flaw was found in all versions of Keycloak before 10.0.0, where the NodeJS adapter did not support the verify-token-audience. This flaw results in some users having access to sensitive information outside of their permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1694
- https://bugzilla.redhat.com/show_bug.cgi?id=1790759
