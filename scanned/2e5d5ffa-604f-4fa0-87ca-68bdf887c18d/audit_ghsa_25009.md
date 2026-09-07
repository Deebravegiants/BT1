# [M] Keycloak Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-3qh2-mccc-q5m6
CVE: CVE-2018-14658
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3qh2-mccc-q5m6
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0

## Details
A flaw was found in JBOSS Keycloak 3.2.1.Final. The Redirect URL for both Login and Logout are not normalized in `org.keycloak.protocol.oidc.utils.RedirectUtils` before the redirect url is verified. This can lead to an Open Redirection attack

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14658
- https://access.redhat.com/errata/RHSA-2018:3592
- https://access.redhat.com/errata/RHSA-2018:3593
- https://access.redhat.com/errata/RHSA-2018:3595
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14658
