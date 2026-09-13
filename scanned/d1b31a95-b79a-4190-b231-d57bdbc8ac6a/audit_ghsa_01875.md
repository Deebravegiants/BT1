# [H] Privilege escalation in the Sulu Admin panel

## Summary
Severity: High
Advisory: GHSA-84px-q68r-2fc9
CVE: CVE-2021-43835
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-15
Source: https://github.com/advisories/GHSA-84px-q68r-2fc9
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=2.0.0 <2.2.18
- Packagist: `sulu/sulu` — affected >=2.3.0 <2.3.8
- Packagist: `sulu/sulu` — affected >=2.4.0-RC1 <2.4.0

## Details
### Impact

Impacted are only users which already have access to the admin UI. Over the API it was possible for them to give themselves permissions to areas which they did not already had. This issue was introduced in 2.0.0-RC1 with the new ProfileController putAction.

### Patches

The versions have been patched in 2.2.18, 2.3.8 and 2.4.0.

### Workarounds

Patching the ProfileController of affected sulu versions yourself by overwriting it.

### References

_Are there any links users can visit to find out more?_

Currently not.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [sulu/sulu repo](https://github.com/sulu/sulu/issues)
* Email us at [security@sulu.io](mailto:security@sulu.io)

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-84px-q68r-2fc9
- https://nvd.nist.gov/vuln/detail/CVE-2021-43835
- https://github.com/sulu/sulu/commit/30bf8b5a4f83b6f2171a696011757d095edaa28a
- https://github.com/sulu/sulu
