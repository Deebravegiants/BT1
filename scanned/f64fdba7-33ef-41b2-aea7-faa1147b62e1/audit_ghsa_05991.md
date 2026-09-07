# [M] Ghost: Member existence leak via magic link sign-in response

## Summary
Severity: Medium
Advisory: GHSA-chgm-3698-jm42
CVE: CVE-2026-53947
CWE: CWE-204
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-chgm-3698-jm42
Type: github-advisory

## Affected
- npm: `ghost` — affected >=5.18.0 <6.21.2

## Details
### Impact

A discrepancy in responses from the members signin endpoints made it possible for an unauthenticated attacker to determine whether a given email address belongs to a registered member of a Ghost site.

### Vulnerable versions

This vulnerability is present in Ghost from v5.18.0 up to v6.21.0.

### Patches

v6.21.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-chgm-3698-jm42
- https://nvd.nist.gov/vuln/detail/CVE-2026-53947
- https://github.com/TryGhost/Ghost/pull/26752
- https://github.com/TryGhost/Ghost/commit/fb2bb634653d99de68fc42d415721d755284fe30
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.21.1
