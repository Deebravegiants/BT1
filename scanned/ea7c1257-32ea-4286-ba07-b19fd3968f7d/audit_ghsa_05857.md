# [M] Ghost Content API filter bypass reveals private fields

## Summary
Severity: Medium
Advisory: GHSA-jx35-x7fj-vgpr
CVE: CVE-2026-53949
CWE: CWE-200, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-jx35-x7fj-vgpr
Type: github-advisory

## Affected
- npm: `ghost` — affected >=5.46.1 <6.21.2

## Details
### Impact

The validation applied to filters on the public API endpoints could be partially bypassed, making it possible to reveal private fields via a brute force attack. If SQLite was used as the database password hashes were fully accessible. If MySQL was used as the database the password hashes' case (uppercase / lowercase) would have been lost, which would likely have rendered a further brute force attack on the discovered hashes fruitless.

### Vulnerable versions

This vulnerability is present in Ghost from v5.46.1 up to v6.21.1.

### Patches

v6.21.2 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### Workarounds

If upgrading immediately is not possible, block or filter requests to Content API endpoints where the `filter` query parameter contains `password` or `email` (including any compound form such as `users.password`, `users.email`, `authors.password`, `authors.email`). Reject requests at a reverse proxy / WAF layer before they reach Ghost.

Example (case-insensitive) pattern to block on the raw querystring:

```
filter=[^&]*(password|email)
```

### References

Ghost thanks crnkovic for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-jx35-x7fj-vgpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-53949
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.21.2
