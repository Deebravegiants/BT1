# [M] Rattler vulnerable to package cache path traversal via conda package build string

## Summary
Severity: Medium
Advisory: GHSA-h672-p7h7-97v9
CVE: CVE-2026-53956
CWE: CWE-22, CWE-73
Ecosystem: PyPI, crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-h672-p7h7-97v9
Type: github-advisory

## Affected
- crates.io: `rattler_cache` — affected >=0 <0.9.0
- PyPI: `py_rattler` — affected >=0 <0.24.0

## Details
`rattler_cache` and `py-rattler` were vulnerable to package-cache path traversal when handling package metadata from conda channels.

During cache materialization, the `ratter_cache` code used the package record `build` string as part of a cache key that was joined into a filesystem path. A malicious or untrusted channel could publish repodata with path separators or traversal components in that field, causing package contents to be written outside the configured package cache directory.

The issue requires use of a malicious or otherwise untrusted conda channel. Curated channels that validate package metadata are not expected to allow malformed build strings of this form.

Users should upgrade to a patched version and avoid untrusted conda channels.

## References
- https://github.com/conda/rattler/security/advisories/GHSA-h672-p7h7-97v9
- https://github.com/conda/rattler
