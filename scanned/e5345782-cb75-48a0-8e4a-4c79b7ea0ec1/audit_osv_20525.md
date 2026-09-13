# [H] CVE-2021-3461

## Summary
Severity: High
Advisory: CVE-2021-3461
Aliases: GHSA-cm29-6wx7-p874
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2022-04-01
Source: https://osv.dev/vulnerability/CVE-2021-3461
Type: osv

## Details
A flaw was found in keycloak where keycloak may fail to logout user session if the logout request comes from external SAML identity provider and Principal Type is set to Attribute [Name].

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1941565
