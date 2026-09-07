# [M] Ghost: Cross-Site Scripting in Universal Import

## Summary
Severity: Medium
Advisory: GHSA-2gx6-7gx2-wwcf
CVE: CVE-2026-70588
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-2gx6-7gx2-wwcf
Type: github-advisory

## Affected
- npm: `ghost` — affected >=5.26.0 <6.54.1

## Details
### Impact

The Universal Import feature in Ghost Admin failed to properly sanitize imported content resulting in XSS in post content.

### Vulnerable versions

This vulnerability is present in Ghost from v5.26.0 up to v6.54.0.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### Workarounds

If upgrading immediately is not possible, avoid using the Universal Import feature.

### References

Ghost thanks meifukun for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-2gx6-7gx2-wwcf
- https://github.com/TryGhost/Ghost/pull/29635
- https://github.com/TryGhost/Ghost/commit/a8bea3a4ceec4c852b880f4885119453c3d8588e
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.54.1
