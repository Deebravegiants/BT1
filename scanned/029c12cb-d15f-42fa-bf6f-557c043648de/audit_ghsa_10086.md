# [M] Keycloak: Arbitrary code execution via Stored Cross-Site Scripting (XSS) in organization selection login page

## Summary
Severity: Medium
Advisory: GHSA-m32f-8vh9-2hh3
CVE: CVE-2026-37980
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-m32f-8vh9-2hh3
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0

## Details
A flaw was found in Keycloak, specifically in the organization selection login page. A remote attacker with `manage-realm` or `manage-organizations` administrative privileges can exploit a Stored Cross-Site Scripting (XSS) vulnerability. This flaw occurs because the `organization.alias` is placed into an inline JavaScript `onclick` handler, allowing a crafted JavaScript payload to execute in a user's browser when they view the login page. Successful exploitation enables arbitrary JavaScript execution, potentially leading to session theft, unauthorized account actions, or further attacks against users of the affected realm.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-37980
- https://github.com/keycloak/keycloak/issues/48049
- https://access.redhat.com/security/cve/CVE-2026-37980
- https://bugzilla.redhat.com/show_bug.cgi?id=2455325
- https://github.com/keycloak/keycloak
