# [M] Ghost: Server-Side Request Forgery Mitigation Issue

## Summary
Severity: Medium
Advisory: GHSA-x5mm-wm4g-j5xv
CVE: CVE-2026-70595
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-x5mm-wm4g-j5xv
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.26.0 <6.54.1

## Details
### Impact

A validation issue allowed some functionality, such as Webmentions, to be abused by an unauthenticated user to make limited HTTP requests to hosts in the Ghost server's internal network. A successful attack would not result in any response data being returned.

### Vulnerable versions

This vulnerability is present in Ghost from v6.26.0 up to v6.54.0.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### References

Ghost thanks Hwang Seyeon for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-x5mm-wm4g-j5xv
- https://github.com/TryGhost/Ghost
