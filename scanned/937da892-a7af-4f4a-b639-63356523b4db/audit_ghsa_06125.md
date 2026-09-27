# [M] Ghost: Theme Upload Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-cjc9-q5gf-327p
CVE: CVE-2026-70593
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-cjc9-q5gf-327p
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0.10.0 <6.54.1

## Details
### Impact

A vulnerability in custom themes allowed a staff user to write files outside of the uploads directory. This could be used to alter the behavior of the installation.

### Vulnerable versions

This vulnerability is present in Ghost from v0.10.0 up to v6.54.0.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### References

Ghost thanks Stephen Sims, Off By One Security for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-cjc9-q5gf-327p
- https://github.com/TryGhost/Ghost/commit/fbaa92327e52607036a1e42204c9eadcc751d82c
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.54.1
