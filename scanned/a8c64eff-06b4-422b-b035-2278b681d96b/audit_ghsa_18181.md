# [M] TinyEnv: Inline comments not stripped properly in .env values

## Summary
Severity: Medium
Advisory: GHSA-72cm-7236-h43r
CVE: CVE-2025-58759
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-72cm-7236-h43r
Type: github-advisory

## Affected
- Packagist: `datahihi1/tiny-env` — affected >=1.0.9 <1.0.11

## Details
### Impact
TinyEnv did not properly strip inline comments inside .env values. This could lead to unexpected behavior or misconfiguration, where variables contain unintended characters (including # or comment text). Applications depending on strict environment values may expose logic errors, insecure defaults, or failed authentication.

### Patches
Fixed in v1.0.11. Users should upgrade to the latest patched version.

### Workarounds
As a temporary workaround, avoid using inline comments in .env files, or sanitize loaded values manually.

## References
- https://github.com/datahihi1/tiny-env/security/advisories/GHSA-72cm-7236-h43r
- https://nvd.nist.gov/vuln/detail/CVE-2025-58759
- https://github.com/datahihi1/tiny-env/commit/69b7b885e6cfbf07f470fb3512360e0caa95521e
- https://github.com/datahihi1/tiny-env
