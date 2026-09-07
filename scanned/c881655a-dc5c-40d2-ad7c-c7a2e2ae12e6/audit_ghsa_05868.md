# [M] Ghost: Cross-Site Scripting in Feature Image Captions

## Summary
Severity: Medium
Advisory: GHSA-pr22-p9rp-2cqv
CVE: CVE-2026-70596
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-pr22-p9rp-2cqv
Type: github-advisory

## Affected
- npm: `ghost` — affected >=4.9.0 <6.54.1

## Details
### Impact

An input validation issue allowed any staff user to create a post with content that could be used to hijack another staff user's Ghost Admin session resulting in privilege escalation.

### Vulnerable versions

This vulnerability is present in Ghost from v4.9.0 up to v6.54.0.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### References

Ghost thanks Versa for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-pr22-p9rp-2cqv
- https://github.com/TryGhost/Ghost/pull/29635
- https://github.com/TryGhost/Ghost/commit/a8bea3a4ceec4c852b880f4885119453c3d8588e
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.54.1
