# [M] Ghost: Server-Side Request Forgery in Image Fetching

## Summary
Severity: Medium
Advisory: GHSA-gcvv-72q8-9v76
CVE: CVE-2026-70591
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-gcvv-72q8-9v76
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0.10.0 <6.54.1

## Details
### Impact

A Server-Side Request Forgery (SSRF) in Ghost Admin allowed any staff-level user to perform a blind HTTP GET request against internal hosts. No output was returned, but this could have been used to probe open ports on internal hosts.

### Vulnerable versions

This vulnerability is present in Ghost from v0.10.0 up to v6.54.0.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### References

Ghost thanks Younghun Ko, vx77, and Miguel Segovia Gil for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-gcvv-72q8-9v76
- https://github.com/TryGhost/Ghost/commit/5eff2de0f477b11c88f20bceb9d184c0d3b8a62e
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.54.1
