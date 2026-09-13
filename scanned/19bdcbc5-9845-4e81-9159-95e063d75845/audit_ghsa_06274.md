# [M] Ghost: Database Backup Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-cj62-hvv2-2q5h
CVE: CVE-2026-70592
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-cj62-hvv2-2q5h
Type: github-advisory

## Affected
- npm: `ghost` — affected >=1.20.1 <6.54.1

## Details
### Impact

An Administrator-level user could remotely overwrite certain files on the filesystem leading to integrity and availability issues.

### Vulnerable versions

This vulnerability is present in Ghost from 1.20.1 up to v6.54.0.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### Workarounds

If upgrading immediately is not possible, set *disableJSBackups* to "true" by running:

```sh
$ ghost config set disableJSBackups true
$ ghost restart
```

### References

Ghost thanks Jorian Woltjer of Aikido Security, Mitchell Benjamin of Revamp Studio, and meifukun for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-cj62-hvv2-2q5h
- https://github.com/TryGhost/Ghost/commit/f466c300191a609ed36c8d7c5d1e33ccd440786b
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.54.1
