# [C] Predictable password in Keycloak

## Summary
Severity: Critical
Advisory: GHSA-6pmv-7pr9-cgrj
CVE: CVE-2020-1731
CWE: CWE-330, CWE-341
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-04-15
Source: https://github.com/advisories/GHSA-6pmv-7pr9-cgrj
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <8.0.2

## Details
A flaw was found in all versions of the Keycloak operator, before version 8.0.2,(community only) where the operator generates a random admin password when installing Keycloak, however the password remains the same when deployed to the same OpenShift namespace.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1731
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1731
