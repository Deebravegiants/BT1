# [H] Improper Verification of SAML Responses Leading to Privilege Escalation in Keycloak

## Summary
Severity: High
Advisory: GHSA-xgfv-xpx8-qhcr
CVE: CVE-2024-8698
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-xgfv-xpx8-qhcr
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-saml-core` — affected >=0 <22.0.13
- Maven: `org.keycloak:keycloak-saml-core` — affected >=23.0.0 <24.0.8
- Maven: `org.keycloak:keycloak-saml-core` — affected >=25.0.0 <25.0.6

## Details
A flaw exists in the SAML signature validation method within the Keycloak XMLSignatureUtil class. The method incorrectly determines whether a SAML signature is for the full document or only for specific assertions based on the position of the signature in the XML document, rather than the Reference element used to specify the signed element. This flaw allows attackers to create crafted responses that can bypass the validation, potentially leading to privilege escalation or impersonation attacks.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-xgfv-xpx8-qhcr
- https://nvd.nist.gov/vuln/detail/CVE-2024-8698
- https://github.com/keycloak/keycloak/releases/tag/25.0.6
- https://github.com/keycloak/keycloak
- https://bugzilla.redhat.com/show_bug.cgi?id=2311641
- https://access.redhat.com/security/cve/CVE-2024-8698
- https://access.redhat.com/errata/RHSA-2024:8826
- https://access.redhat.com/errata/RHSA-2024:8824
- https://access.redhat.com/errata/RHSA-2024:8823
- https://access.redhat.com/errata/RHSA-2024:6890
- https://access.redhat.com/errata/RHSA-2024:6889
- https://access.redhat.com/errata/RHSA-2024:6888
- https://access.redhat.com/errata/RHSA-2024:6887
- https://access.redhat.com/errata/RHSA-2024:6886
- https://access.redhat.com/errata/RHSA-2024:6882
- https://access.redhat.com/errata/RHSA-2024:6880
- https://access.redhat.com/errata/RHSA-2024:6879
- https://access.redhat.com/errata/RHSA-2024:6878
