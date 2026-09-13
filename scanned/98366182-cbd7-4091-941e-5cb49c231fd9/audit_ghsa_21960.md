# [H] Improper Input Validation in Keycloak

## Summary
Severity: High
Advisory: GHSA-m6mm-q862-j366
CVE: CVE-2020-1714
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-m6mm-q862-j366
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <11.0.0
- Maven: `org.keycloak:keycloak-common` — affected >=0 <11.0.0

## Details
A flaw was found in Keycloak before version 11.0.0, where the code base contains usages of ObjectInputStream without type checks. This flaw allows an attacker to inject arbitrarily serialized Java Objects, which would then get deserialized in a privileged context and potentially lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1714
- https://github.com/keycloak/keycloak/pull/7053
- https://github.com/keycloak/keycloak/commit/33863ba16117844930a38ebde57a25258f5b80fd
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1714
- https://github.com/keycloak/keycloak
