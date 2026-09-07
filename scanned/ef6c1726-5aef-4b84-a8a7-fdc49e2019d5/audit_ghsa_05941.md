# [M] Ghost: Blind Password Hash Disclosure in Ghost Admin API

## Summary
Severity: Medium
Advisory: GHSA-jm22-3w23-5q7w
CVE: CVE-2026-70590
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-jm22-3w23-5q7w
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0 <6.54.1

## Details
### Impact

Any staff-level user was able to leak the hashed passwords of other staff users. An offline password-guessing attack against the hashes could lead to account takeover if successful, but [Device Verification](https://docs.ghost.org/security#device-verification) should have prevented an attacker from logging in with a recovered password. Depending on the database used, leaked hashes may not have had the correct casing for all characters, increasing the difficulty of a password-guessing attack.

### Vulnerable versions

This vulnerability is present in Ghost versions v6.54.0 and earlier.

### Patches

v6.54.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### Workarounds

If upgrading immediately is not possible, ensure all staff users have [Multi-factor Authentication](https://docs.ghost.org/security#email-2fa) (MFA) enabled. This will help prevent an attacker from logging in with any passwords that are successfully recovered from the leaked hashes.

### References

Ghost thanks Chapman Schleiss for disclosing this vulnerability responsibly. 

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-jm22-3w23-5q7w
- https://github.com/TryGhost/Ghost/pull/29628
- https://github.com/TryGhost/Ghost/commit/63c31fad7e473caa62d8fbb4651a04a2a62b5d00
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.54.1
