# [M] Parse Server vulnerable to LDAP injection via unsanitized user input in DN and group filter construction

## Summary
Severity: Medium
Advisory: GHSA-7m6r-fhh7-r47c
CVE: CVE-2026-31828
CWE: CWE-90
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-7m6r-fhh7-r47c
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.2-alpha.13
- npm: `parse-server` — affected >=0 <8.6.26

## Details
### Impact

The LDAP authentication adapter is vulnerable to LDAP injection. User-supplied input (`authData.id`) is interpolated directly into LDAP Distinguished Names (DN) and group search filters without escaping special characters. This allows an attacker with valid LDAP credentials to manipulate the bind DN structure and to bypass group membership checks. This enables privilege escalation from any authenticated LDAP user to a member of any restricted group.

The vulnerability affects Parse Server deployments that use the LDAP authentication adapter with group-based access control.

### Patches

The vulnerability is fixed by escaping user input before interpolation into DN strings (per [RFC 4514](https://datatracker.ietf.org/doc/html/rfc4514#section-2.4)) and LDAP filter strings (per [RFC 4515](https://datatracker.ietf.org/doc/html/rfc4515#section-3)).

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-7m6r-fhh7-r47c
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.13
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.26

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-7m6r-fhh7-r47c
- https://nvd.nist.gov/vuln/detail/CVE-2026-31828
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.26
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.13
