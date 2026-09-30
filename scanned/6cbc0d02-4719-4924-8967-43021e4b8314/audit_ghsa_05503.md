# [H] Ghost has Staff Token permission bypass

## Summary
Severity: High
Advisory: GHSA-9xg7-mwmp-xmjx
CVE: CVE-2026-22595
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-9xg7-mwmp-xmjx
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.0.0 <6.11.0
- npm: `ghost` — affected >=5.105.0 <5.130.6

## Details
### Impact
A vulnerability in Ghost's handling of Staff Token authentication allowed certain endpoints to be accessed that were only intended to be accessible via Staff Session authentication. External systems that have been authenticated via Staff Tokens for Admin/Owner-role users would have had access to these endpoints. 

### Vulnerable versions
This vulnerability is present in Ghost v5.121.0 to v5.130.5 to and Ghost v6.0.0 to v6.10.3.

### Patches
v5.130.6 and v6.11.0 contain a fix for this issue.

### References
Ghost thanks Sho Odagiri of GMO Cybersecurity by Ierae, Inc. for discovering and disclosing this vulnerability responsibly.

### For more information
If there are any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-9xg7-mwmp-xmjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-22595
- https://github.com/TryGhost/Ghost/commit/9513d2a35c21067127ce8192443d8919ddcefcc8
- https://github.com/TryGhost/Ghost/commit/c3017f81a5387b253a7b8c1ba1959d430ee536a3
- https://github.com/TryGhost/Ghost
