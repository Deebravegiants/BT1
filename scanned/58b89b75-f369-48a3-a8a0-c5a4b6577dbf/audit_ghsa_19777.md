# [M] Keycloak Denial of Service (DoS) Vulnerability via JWT Token Cache

## Summary
Severity: Medium
Advisory: GHSA-2935-2wfm-hhpv
CVE: CVE-2025-2559
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-2935-2wfm-hhpv
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0

## Details
A flaw was found in Keycloak. When the configuration uses JWT tokens for authentication, the tokens are cached until expiration. If a client uses JWT tokens with an excessively long expiration time, for example, 24 or 48 hours, the cache can grow indefinitely, leading to an OutOfMemoryError. This issue could result in a denial of service condition, preventing legitimate users from accessing the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2559
- https://access.redhat.com/errata/RHSA-2025:4335
- https://access.redhat.com/errata/RHSA-2025:4336
- https://access.redhat.com/security/cve/CVE-2025-2559
- https://bugzilla.redhat.com/show_bug.cgi?id=2353868
- https://github.com/keycloak/keycloak
