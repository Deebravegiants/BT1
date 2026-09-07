# [H] Keycloak: Open redirect when using wildcard valid redirect URIs in Keycloak

## Summary
Severity: High
Advisory: GHSA-rp95-xpg9-c2cq
CVE: CVE-2026-7504
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-rp95-xpg9-c2cq
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.2

## Details
A flaw was found in Keycloak's URL validation logic during redirect operations. By crafting a malicious request, an attacker could bypass validation to redirect users to unauthorized URLs, potentially leading to the exposure of sensitive information within the domain or facilitating further attacks. This vulnerability specifically affects Keycloak clients configured with a wildcard (*) in the "Valid Redirect URIs" field and requires user interaction to be successfully exploited.

The issue stems from a discrepancy in how Keycloak and the underlying Java URI implementation handle the user-info component of a URL. If a malicious redirect URL is constructed using multiple @ characters in the user-info section, Java's URI parser fails to extract the user-info, leaving only the raw authority field. Consequently, Keycloak's validation check fails to detect the malformed user-info, falls back to a wildcard comparison, and incorrectly permits the malicious redirect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7504
- https://github.com/keycloak/keycloak/pull/49130
- https://github.com/keycloak/keycloak/commit/479620769073ac36b782dee65086ab35e8e5d14e
- https://access.redhat.com/errata/RHSA-2026:19594
- https://access.redhat.com/errata/RHSA-2026:19595
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-7504
- https://bugzilla.redhat.com/show_bug.cgi?id=2464128
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.6.2
