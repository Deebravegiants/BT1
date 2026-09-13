# [C] Parse Server: Account takeover via operator injection in authentication data identifier

## Summary
Severity: Critical
Advisory: GHSA-5fw2-8jcv-xh87
CVE: CVE-2026-32248
CWE: CWE-943
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-5fw2-8jcv-xh87
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.12
- npm: `parse-server` — affected >=0 <8.6.38

## Details
### Impact

An unauthenticated attacker can take over any user account that was created with an authentication provider that does not validate the format of the user identifier (e.g. anonymous authentication). By sending a crafted login request, the attacker can cause the server to perform a pattern-matching query instead of an exact-match lookup, allowing the attacker to match an existing user and obtain a valid session token for that user's account. Both MongoDB and PostgreSQL database backends are affected. Any Parse Server deployment that allows anonymous authentication (enabled by default) is vulnerable.

### Patches

The fix enforces that the user identifier in authentication data is a string before using it in a database query. Non-string values are rejected with a validation error.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-5fw2-8jcv-xh87
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.12
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.38

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-5fw2-8jcv-xh87
- https://nvd.nist.gov/vuln/detail/CVE-2026-32248
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.38
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.12
