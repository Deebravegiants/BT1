# [H] Privilege Defined With Unsafe Actions in Keycloak

## Summary
Severity: High
Advisory: GHSA-7m27-3587-83xf
CVE: CVE-2019-10170
CWE: CWE-267
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-21
Source: https://github.com/advisories/GHSA-7m27-3587-83xf
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <8.0.0

## Details
A flaw was found in the Keycloak admin console, where the realm management interface permits a script to be set via the policy. This flaw allows an attacker with authenticated user and realm management permissions to configure a malicious script to trigger and execute arbitrary code with the permissions of the application user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10170
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10170
- https://github.com/keycloak/keycloak
