# [C] Parse Server vulnerable to session token exfiltration via `redirectClassNameForKey` query parameter

## Summary
Severity: Critical
Advisory: GHSA-6r2j-cxgf-495f
CVE: CVE-2026-30965
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-6r2j-cxgf-495f
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.2-alpha.8
- npm: `parse-server` — affected >=0 <8.6.21

## Details
### Impact

A vulnerability in Parse Server's query handling allows an authenticated or unauthenticated attacker to exfiltrate session tokens of other users by exploiting the `redirectClassNameForKey` query parameter. Exfiltrated session tokens can be used to take over user accounts.

The vulnerability requires the attacker to be able to create or update an object with a new relation field, which depends on the Class-Level Permissions of at least one class.

### Patches

The fix applies the same security checks that normally protect class access after the query redirect, ensuring that queries redirected via `redirectClassNameForKey` are subject to the same restrictions as direct queries to the target class.

### Workarounds

Set restrictive Class-Level Permissions to prevent clients from creating new fields on classes, specifically by disabling `addField` for public access and unauthenticated users. Note that this limits client functionality and does not fully eliminate the risk if a relation field pointing to a protected class already exists in the schema.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-6r2j-cxgf-495f
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.8
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.21

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-6r2j-cxgf-495f
- https://nvd.nist.gov/vuln/detail/CVE-2026-30965
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.21
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.8
