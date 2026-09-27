# [H] Incorrect implementation of lockout feature in Keycloak

## Summary
Severity: High
Advisory: GHSA-xv7h-95r7-595j
CVE: CVE-2021-3513
CWE: CWE-209, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-23
Source: https://github.com/advisories/GHSA-xv7h-95r7-595j
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <13.0.0

## Details
A flaw was found in keycloak where a brute force attack is possible even when the permanent lockout feature is enabled. This is due to a wrong error message displayed when wrong credentials are entered. The highest threat from this vulnerability is to confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3513
- https://github.com/keycloak/keycloak/pull/7976
- https://access.redhat.com/security/cve/CVE-2021-3513
- https://bugzilla.redhat.com/show_bug.cgi?id=1953439
- https://github.com/keycloak/keycloak
