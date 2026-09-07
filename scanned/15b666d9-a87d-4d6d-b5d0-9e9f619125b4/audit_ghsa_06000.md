# [H] XSS in Ghost's ActivityPub client

## Summary
Severity: High
Advisory: GHSA-xpp7-93x6-v29m
CVE: CVE-2026-53950
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-xpp7-93x6-v29m
Type: github-advisory

## Affected
- npm: `@tryghost/activitypub` — affected >=0 <3.1.0

## Details
### Impact

The ActivityPub client in Ghost was vulnerable to JavaScript injection on posts shared by a maliciously customised ActivityPub server.

### Vulnerable Versions

This vulnerability is present in the @tryghost/activitypub package up to v3.0.8. All prior versions are also affected. 

### Patches

@tryghost/activitypub v3.1.0 contains a fix for this issue and is also automatically fetched by Ghost.

### References

Ghost thanks Brad Geesaman, Ghost Security for disclosing this vulnerability responsibly. 

### For more information

If you have any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-xpp7-93x6-v29m
- https://nvd.nist.gov/vuln/detail/CVE-2026-53950
- https://github.com/TryGhost/Ghost
