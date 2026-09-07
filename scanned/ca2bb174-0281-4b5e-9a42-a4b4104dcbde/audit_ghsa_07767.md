# [M] unity-cli Exposes Plaintext Credentials in Debug Logs (sign-package command)

## Summary
Severity: Medium
Advisory: GHSA-4255-c27h-62m5
CVE: CVE-2026-25918
CWE: CWE-352, CWE-532
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-4255-c27h-62m5
Type: github-advisory

## Affected
- npm: `@rage-against-the-pixel/unity-cli` — affected >=0 <1.8.2

## Details
The sign-package command in @rage-against-the-pixel/unity-cli logs sensitive credentials in plaintext when the `--verbose` flag is used. Command-line arguments including `--email` and `--password` are output via JSON.stringify without sanitization, exposing secrets to shell history, CI/CD logs, and log aggregation systems.

Users who run sign-package with `--verbose` and credential arguments expose their Unity account passwords. This affects all versions prior to 1.8.2. The vulnerability requires explicit user action (using `--verbose`) but creates significant risk in automated and shared environments.

Workaround: Use environment variables (`UNITY_USERNAME`, `UNITY_PASSWORD`) instead of command-line arguments, and avoid the `--verbose` flag when working with credentials.

Existing RageAgainstThePixel and Buildalon GitHub actions are unaffected as they use the environment variables exclusively.

## References
- https://github.com/RageAgainstThePixel/unity-cli/security/advisories/GHSA-4255-c27h-62m5
- https://nvd.nist.gov/vuln/detail/CVE-2026-25918
- https://github.com/RageAgainstThePixel/unity-cli/commit/8d4d67b23d7c5fd8f00df3f0f10bec2961c95342
- https://github.com/RageAgainstThePixel/unity-cli
- https://github.com/RageAgainstThePixel/unity-cli/releases/tag/v1.8.2
