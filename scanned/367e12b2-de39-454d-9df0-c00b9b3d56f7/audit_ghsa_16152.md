# [M] Keycloak proxy header handling Denial-of-Service (DoS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jgwc-jh89-rpgq
CVE: CVE-2024-9666
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-jgwc-jh89-rpgq
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=0
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=25.0.0 <26.0.6

## Details
Keycloak versions 26 and earlier are vulnerable to a denial-of-service (DoS) attack through improper handling of proxy headers. When Keycloak is configured to accept incoming proxy headers, it may accept non-IP values, such as obfuscated identifiers, without proper validation. This can lead to costly DNS resolution operations, which an attacker could exploit to tie up IO threads and potentially cause a denial of service.

The attacker must have access to send requests to a Keycloak instance that is configured to accept proxy headers, specifically when reverse proxies do not overwrite incoming headers, and Keycloak is configured to trust these headers.

For Keycloak version 26, for successful exploitation includes: the realm must have SslRequired=EXTERNAL (the default), HTTP must be enabled, the instance must not be using a full hostname URL, access must come from behind a proxy (assuming the proxy overwrites the X-Forwarded-For header), and trusted proxies must not be set or must incorrectly trust the client from which the request is originating.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-jgwc-jh89-rpgq
- https://nvd.nist.gov/vuln/detail/CVE-2024-9666
- https://github.com/keycloak/keycloak/issues/35216
- https://access.redhat.com/errata/RHSA-2024:10175
- https://access.redhat.com/errata/RHSA-2024:10176
- https://access.redhat.com/errata/RHSA-2024:10177
- https://access.redhat.com/errata/RHSA-2024:10178
- https://access.redhat.com/security/cve/CVE-2024-9666
- https://bugzilla.redhat.com/show_bug.cgi?id=2317440
- https://github.com/keycloak/keycloak
