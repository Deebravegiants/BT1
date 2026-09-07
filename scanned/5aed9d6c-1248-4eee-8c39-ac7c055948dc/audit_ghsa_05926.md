# [M] Ghost: File Upload Content-Type Spoofing

## Summary
Severity: Medium
Advisory: GHSA-944x-pm95-3jpr
CVE: CVE-2026-53948
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-944x-pm95-3jpr
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.19.4 <6.21.1

## Details
### Impact

Insufficient validation of the client-supplied `Content-Type` on Ghost's Admin API file upload endpoint allowed uploaded files to be served from the site with an attacker-chosen content type on S3/GCS storage backends. On installations that serve uploaded files from the same origin as the site, this could have been used to facilitate stored cross-site scripting against site visitors or staff.

### Vulnerable versions

This vulnerability is present in Ghost from v6.19.4 up to v6.21.0.

### Patches

v6.21.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-944x-pm95-3jpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-53948
- https://github.com/TryGhost/Ghost/pull/26751
- https://github.com/TryGhost/Ghost/commit/d659e752d6636144d75b9aa94062cdbc88a16b21
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.21.1
