# [M] @steipete/summarize allows local attackers to read bearer tokens and API credentials stored in ~/.summarize/daemon.json

## Summary
Severity: Medium
Advisory: GHSA-qp7v-gjgg-4mj6
CVE: CVE-2026-45222
CWE: CWE-732
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-qp7v-gjgg-4mj6
Type: github-advisory

## Affected
- npm: `@steipete/summarize` — affected >=0 <0.15.0

## Details
Summarize versions through 0.14.1, fixed in commit 0cfb0fb, creates the daemon configuration directory and file with default filesystem permissions that may be world-readable on Unix-like systems, allowing local attackers to read bearer tokens and API credentials stored in ~/.summarize/daemon.json. A local attacker can exploit these permissive permissions to read the daemon bearer token and persisted provider credentials, enabling unauthorized access to the daemon or recovery of sensitive API keys.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45222
- https://github.com/steipete/summarize/pull/214
- https://github.com/steipete/summarize/commit/0cfb0fb99777a87a7b02082b5e4bd449f8dd6175
- https://github.com/steipete/summarize
- https://github.com/steipete/summarize/releases/tag/v0.15.0
- https://www.vulncheck.com/advisories/summarize-insecure-daemon-configuration-file-permissions
