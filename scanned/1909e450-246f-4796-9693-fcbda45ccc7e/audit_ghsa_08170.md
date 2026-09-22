# [M] Keycloak logs sensitive headers

## Summary
Severity: Medium
Advisory: GHSA-gv3v-2cpp-3pmq
CVE: CVE-2025-11537
CWE: CWE-117
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-gv3v-2cpp-3pmq
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=0 <26.5.6

## Details
A flaw was found in Keycloak. When the logging format is configured to a verbose, user-supplied pattern (such as the pre-defined 'long' pattern), sensitive headers including Authorization and Cookie are disclosed to the logs in cleartext. An attacker with read access to the log files can extract these credentials (e.g., bearer tokens, session cookies) and use them to impersonate users, leading to a full account compromise.

Patches are available, see:

- https://github.com/keycloak/keycloak/releases/tag/26.4.11
- https://github.com/keycloak/keycloak/releases/tag/26.5.6
- https://github.com/keycloak/keycloak/releases/tag/26.6.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11537
- https://github.com/keycloak/keycloak/commit/137a35c1109ff43a305f26264978a3ea21452373
- https://github.com/keycloak/keycloak/commit/5a3cdb7c4ccbf83ffc926f70d655a60269d7207b
- https://github.com/keycloak/keycloak/commit/9622f550a6e565b29a3a37454421f08626791a6c
- https://access.redhat.com/security/cve/CVE-2025-11537
- https://bugzilla.redhat.com/show_bug.cgi?id=2402616
- https://github.com/keycloak/keycloak
- https://www.keycloak.org/server/logging#_change_log_formatpattern
