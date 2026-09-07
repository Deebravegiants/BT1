# [H] Ghost vulnerable to XSS via malicious Portal preview links

## Summary
Severity: High
Advisory: GHSA-gv6q-2m97-882h
CVE: CVE-2026-24778
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-gv6q-2m97-882h
Type: github-advisory

## Affected
- npm: `ghost` — affected >=5.43.0 <5.121.0
- npm: `@tryghost/portal` — affected >=2.29.1 <2.51.5
- npm: `@tryghost/portal` — affected >=2.52.0 <2.57.1
- npm: `ghost` — affected >=6.0.0 <6.15.0

## Details
### Impact
An attacker was able to craft a malicious link that, when accessed by an authenticated staff user or member, would execute JavaScript with the victim's permissions, potentially leading to account takeover. 

### Vulnerable versions
This vulnerability is present in Ghost versions:
- v5.43.0 to v5.120.4
- v6.0.0 to v6.14.0

As well as in Portal versions:
- v2.29.1 to v2.51.4
- v2.52.0 to v2.57.0

### Patches
Ghost automatically loads the latest patch of the members Portal component via CDN. Therefore:
- For Ghost 5.x users, upgrading to v5.121.0 or later fixes the vulnerability (loads Portal v2.51.5, which contains the patch)
- For Ghost 6.x users, upgrading to v6.15.0 or later fixes the vulnerability (loads Portal v2.57.1, which contains the patch)

For Ghost installations using a customised or self-hosted version of Portal, it will be necessary to manually rebuild from or update to the latest patch version.

### References
Ghost thanks Younes Belalia for discovering and disclosing this vulnerability responsibly.

### For more information
If users have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-gv6q-2m97-882h
- https://nvd.nist.gov/vuln/detail/CVE-2026-24778
- https://github.com/TryGhost/Ghost/commit/da858e640e88e69c1773a7b7ecdc2008fa143849
- https://github.com/TryGhost/Ghost
