# [H] Keycloak: path traversal in the redirect validation

## Summary
Severity: High
Advisory: CVE-2024-2419
Aliases: GHSA-mrv8-pqfj-7gp5
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-2419
Type: osv

## Details
A flaw was found in Keycloak's redirect_uri validation logic. This issue may allow a bypass of otherwise explicitly allowed hosts. A successful attack may lead to the theft of an access token, making it possible for the attacker to impersonate other users. It is very similar to CVE-2023-6291.

## References
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2024:1867
- https://access.redhat.com/security/cve/CVE-2024-2419
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2419.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2419
- https://bugzilla.redhat.com/show_bug.cgi?id=2269371
- https://github.com/keycloak/keycloak
