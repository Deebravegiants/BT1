# [M] Ghost: Session Fixation in Ghost Admin

## Summary
Severity: Medium
Advisory: GHSA-7mpp-r37j-x5wh
CVE: CVE-2026-70594
CWE: CWE-384
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-7mpp-r37j-x5wh
Type: github-advisory

## Affected
- npm: `ghost` — affected >=2.2.0 <6.54.1

## Details
### Impact

Ghost Admin did not invalidate existing sessions on login which could have allowed for session fixation attacks. Successful exploitation would have required another vulnerability on the same domain where Ghost Admin was hosted.

### Vulnerable versions

This vulnerability is present in Ghost from v2.2.0 to v6.54.0.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### References

Ghost thanks meifukun for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-7mpp-r37j-x5wh
- https://github.com/TryGhost/Ghost/pull/29634
- https://github.com/TryGhost/Ghost/commit/6b1c85c30dd0bacb4d5ffe64fc675ac9342d800c
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.54.1
