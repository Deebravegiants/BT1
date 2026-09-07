# [M] Keycloak vulnerable to log Injection during WebAuthn authentication or registration

## Summary
Severity: Medium
Advisory: GHSA-j628-q885-8gr5
CVE: CVE-2023-6484
CWE: CWE-117
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-j628-q885-8gr5
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.9
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <23.0.5

## Details
A flaw was found in keycloak 22.0.5. Errors in browser client during setup/auth with "Security Key login" (WebAuthn) are written into the form, send to Keycloak and logged without escaping allowing log injection.

Acknowledgements:
Special thanks toTheresa Henze for reporting this issue and helping us improve our security.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-j628-q885-8gr5
- https://nvd.nist.gov/vuln/detail/CVE-2023-6484
- https://github.com/keycloak/keycloak/issues/25078
- https://github.com/keycloak/keycloak/commit/f9049565a9a228faa08138b9269d66d3de6c7e9a
- https://github.com/keycloak/keycloak/commit/110f64a8146d0817252f90cf4b5e6a62aa897aff
- https://github.com/keycloak/keycloak
- https://github.com/advisories/GHSA-j628-q885-8gr5
- https://bugzilla.redhat.com/show_bug.cgi?id=2248423
- https://access.redhat.com/security/cve/CVE-2023-6484
- https://access.redhat.com/errata/RHSA-2024:1868
- https://access.redhat.com/errata/RHSA-2024:1867
- https://access.redhat.com/errata/RHSA-2024:1866
- https://access.redhat.com/errata/RHSA-2024:1865
- https://access.redhat.com/errata/RHSA-2024:1864
- https://access.redhat.com/errata/RHSA-2024:1862
- https://access.redhat.com/errata/RHSA-2024:1861
- https://access.redhat.com/errata/RHSA-2024:1860
- https://access.redhat.com/errata/RHSA-2024:0804
- https://access.redhat.com/errata/RHSA-2024:0801
- https://access.redhat.com/errata/RHSA-2024:0800
