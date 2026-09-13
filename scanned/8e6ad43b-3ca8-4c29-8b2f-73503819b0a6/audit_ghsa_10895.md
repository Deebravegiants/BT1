# [M] Sprig Plugin for Craft CMS potentially discloses sensitive information via Sprig Playground

## Summary
Severity: Medium
Advisory: GHSA-m59h-42jf-cphr
CVE: CVE-2026-27131
CWE: CWE-200, CWE-489
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-m59h-42jf-cphr
Type: github-advisory

## Affected
- Packagist: `putyourlightson/craft-sprig` — affected >=2.0.0 <2.15.2
- Packagist: `putyourlightson/craft-sprig` — affected >=3.0.0 <3.7.2

## Details
Admin users, and users with explicit permission to access the Sprig Playground, could potentially expose the security key, credentials, and other sensitive configuration data, in addition to running the `hashData()` signing function.

This issue was mitigated in versions 3.7.2 and 2.15.2 by disabling access to the Sprig Playground entirely when `devMode` is disabled, by default. It is possible to override this behaviour using a new `enablePlaygroundWhenDevModeDisabled` that defaults to `false`.

References:

- https://github.com/putyourlightson/craft-sprig/commit/db18c46f6dc5603828aa321a3a615adbd677d475
- https://github.com/putyourlightson/craft-sprig/commit/09c9da2ffb45a8857829f3390ae2578e26cfe03b

## References
- https://github.com/putyourlightson/craft-sprig/security/advisories/GHSA-m59h-42jf-cphr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27131
- https://github.com/putyourlightson/craft-sprig/commit/09c9da2ffb45a8857829f3390ae2578e26cfe03b
- https://github.com/putyourlightson/craft-sprig/commit/db18c46f6dc5603828aa321a3a615adbd677d475
- https://github.com/putyourlightson/craft-sprig
