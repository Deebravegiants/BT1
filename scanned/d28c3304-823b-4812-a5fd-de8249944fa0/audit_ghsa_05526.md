# [H] Ghost has Staff 2FA bypass

## Summary
Severity: High
Advisory: GHSA-5fp7-g646-ccf4
CVE: CVE-2026-22594
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-5fp7-g646-ccf4
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.0.0 <6.11.0
- npm: `ghost` — affected >=5.105.0 <5.130.6

## Details
### Impact
A vulnerability in Ghost's 2FA mechanism allows staff users to skip email 2FA.

### Vulnerable versions
This vulnerability is present in Ghost v5.105.0 to v5.130.5 to and Ghost v6.0.0 to v6.10.3.

### Patches
v5.130.6 and v6.11.0 contain a fix for this issue.

### References
Ghost thanks Sho Odagiri of GMO Cybersecurity by Ierae, Inc. for discovering and disclosing this vulnerability responsibly.

### For more information
If there are any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-5fp7-g646-ccf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22594
- https://github.com/TryGhost/Ghost/commit/b59f707f670e6f175b669977724ccf16c718430b
- https://github.com/TryGhost/Ghost/commit/fc7bc2fb0888513498154ec5cb4b21eccb88de07
- https://github.com/TryGhost/Ghost
