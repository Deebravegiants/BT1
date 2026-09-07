# [M] Keycloak vulnerable to cross-site scripting via the state parameter

## Summary
Severity: Medium
Advisory: GHSA-458h-wv48-fq75
CVE: CVE-2018-14655
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-458h-wv48-fq75
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0
- Maven: `org.keycloak:keycloak-parent` — affected >=4.0.0.Beta1
- Maven: `org.keycloak:keycloak-parent` — affected 4.3.0.Final

## Details
A flaw was found in Keycloak 3.4.3.Final, 4.0.0.Beta2, 4.3.0.Final. When using `response_mode=form_post` it is possible to inject arbitrary Javascript-Code via the 'state'-parameter in the authentication URL. This allows an XSS-Attack upon succesfully login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14655
- https://access.redhat.com/errata/RHSA-2018:3592
- https://access.redhat.com/errata/RHSA-2018:3593
- https://access.redhat.com/errata/RHSA-2018:3595
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14655
- https://github.com/keycloak/keycloak
