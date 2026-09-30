# [M] Ghost: Private IP filtering bypass to make server-side requests to internal services

## Summary
Severity: Medium
Advisory: GHSA-wvp2-4qqp-4h3r
CVE: CVE-2026-53944
CWE: CWE-184, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-wvp2-4qqp-4h3r
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.0.9 <6.21.1

## Details
### Impact

When making an external request, it is possible to bypass the IP filter that ensures the request isn't going to an internal service using an IPv6 literal which maps to a private IPv4 address.

### Vulnerable versions

This vulnerability is present in Ghost from v6.0.9 up to v6.21.0.

### Patches

v6.21.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### References

Ghost thanks [l3tchupkt](http://github.com/l3tchupkt) for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-wvp2-4qqp-4h3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-53944
- https://github.com/TryGhost/Ghost/pull/26749
- https://github.com/TryGhost/Ghost/commit/9b7f2212970fade08ecbec543b405190471e38d4
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.21.1
