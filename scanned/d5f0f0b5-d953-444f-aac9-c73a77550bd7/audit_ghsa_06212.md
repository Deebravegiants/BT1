# [M] Ghost: Archived Offers can be Redeemed

## Summary
Severity: Medium
Advisory: GHSA-4wx2-7gvj-qfq3
CVE: CVE-2026-70589
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-4wx2-7gvj-qfq3
Type: github-advisory

## Affected
- npm: `ghost` — affected >=4.22.0 <6.54.1

## Details
### Impact

A missing validation check allowed users to redeem subscription offers that were no longer active.

### Vulnerable versions

This vulnerability is present in Ghost from v4.22.0 up to v6.54.0.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### References

Ghost thanks Pedro Pinho for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-4wx2-7gvj-qfq3
- https://github.com/TryGhost/Ghost/commit/d91c0fc52dfc987d71a9803dbcbe6447d21b92fb
- https://github.com/TryGhost/Ghost
