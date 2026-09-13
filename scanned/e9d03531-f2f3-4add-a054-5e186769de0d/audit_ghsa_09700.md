# [H] Kedro: Path Traversal in versioned dataset loading via unsanitized version string

## Summary
Severity: High
Advisory: GHSA-6326-w46w-ppjw
CVE: CVE-2026-35167
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-6326-w46w-ppjw
Type: github-advisory

## Affected
- PyPI: `kedro` — affected >=0 <1.3.0

## Details
### Impact
The `_get_versioned_path()` method in kedro/io/core.py constructs filesystem paths by directly interpolating user-supplied version strings without sanitization. Because version strings are used as path components, traversal sequences such as ../ are preserved and can escape the intended versioned dataset directory.
This is reachable through multiple entry points: `catalog.load(..., version=...)`, `DataCatalog.from_config(..., load_versions=...)`, and the CLI via `kedro run --load-versions=dataset:../../../secrets`. An attacker who can influence the version string can force Kedro to load files from outside the intended version directory, enabling unauthorized file reads, data poisoning, or cross-tenant data access in shared environments.

### Patches
Yes. Fixed in kedro version 1.3.0. Users should upgrade to kedro >= 1.3.0.

### Workarounds
Validate version strings before passing them to DataCatalog or the CLI, ensuring they do not contain `..` segments, path separators, or absolute paths.

## References
- https://github.com/kedro-org/kedro/security/advisories/GHSA-6326-w46w-ppjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-35167
- https://github.com/kedro-org/kedro/pull/5442
- https://github.com/kedro-org/kedro
- https://github.com/pypa/advisory-database/tree/main/vulns/kedro/PYSEC-2026-71.yaml
