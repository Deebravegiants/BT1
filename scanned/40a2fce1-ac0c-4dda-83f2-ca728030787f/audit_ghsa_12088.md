# [H] Ghost has incomplete CSRF protections around OTC use

## Summary
Severity: High
Advisory: GHSA-9m84-wc28-w895
CVE: CVE-2026-29784
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-9m84-wc28-w895
Type: github-advisory

## Affected
- npm: `ghost` — affected >=5.101.6 <6.19.3

## Details
### Impact

Incomplete CSRF protections around `/session/verify` made it possible to use OTCs in login sessions different from the requesting session. In some scenarios this might have made it easier for phishers to take over a Ghost site. 

### Vulnerable versions

This vulnerability is present in Ghost from v5.101.6 up to v6.19.2.

### Patches

v6.19.3 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If a project's Ghost is a Ghost-CLI install see the documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### For more information

If there are any questions or comments about this advisory, send an email to [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-9m84-wc28-w895
- https://nvd.nist.gov/vuln/detail/CVE-2026-29784
- https://github.com/TryGhost/Ghost/commit/ec065a774fa125953d2aa644a59cd8990329e0a0
- https://github.com/TryGhost/Ghost
