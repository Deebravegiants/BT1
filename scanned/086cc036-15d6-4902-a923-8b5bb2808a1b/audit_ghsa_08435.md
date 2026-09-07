# [M] ogham-mcp had credentials embedded in published PyPI sdists -- Neon postgres URLs and Voyage API key

## Summary
Severity: Medium
Advisory: GHSA-8pqq-224h-x875
CWE: CWE-798
Ecosystem: PyPI
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-8pqq-224h-x875
Type: github-advisory

## Affected
- PyPI: `ogham-mcp` — affected >=0.6.3 <0.11.1

## Details
## Summary

Between 2026-02 and 2026-04-24 a total of 22 public PyPI sdists of `ogham-mcp` contained development credentials embedded in source files. All credentials have since been rotated on the respective providers. No known exploitation. Upgrade to **v0.11.1** to get a clean release.

## What was leaked

| Credential | Location in sdist | Vulnerable range | Count |
|---|---|---|---|
| 3x Neon postgres URLs with passwords (US / EU / AP development databases) | top-level `Makefile` (`NEON_US`, `NEON_EU`, `NEON_AP` vars) | `>=0.6.5, <0.11.0` | 21 sdists |
| 1x Voyage AI API key (`pa-...`) | `tests/test_hooks.py::test_mask_secrets_key_value` -- test fixture that fed a real key into the redaction-function tester | `>=0.6.3, <0.11.1` | 22 sdists |

## Impact

- **Primary risk**: any consumer of the affected sdists could have extracted the credentials and used them. The Neon URLs pointed at development databases; the Voyage key was a rate-limited API key.
- **Observed exploitation**: none detected. Audit logs on both providers were reviewed post-rotation.
- **Remediation on our side**:
  - Neon passwords for all three regions rotated.
  - Voyage API key rotated.
  - All affected versions yanked from PyPI (v0.3.0 through v0.10.4 yanked on 2026-04-24; v0.11.0 pending yank after this advisory).
  - v0.11.0 removed the Neon URLs and introduced `make publish-check` which scans every sdist for credential patterns before upload.
  - v0.11.1 scrubs the Voyage key from the test fixture and excludes `benchmarks/`, `docs/`, `research/`, `extras/`, and `**/*.env*` from all future sdists via explicit hatchling sdist include/exclude in `pyproject.toml`.

## Action for users

- If users installed any version from `v0.3.0` through `v0.11.0`, upgrade to **v0.11.1** immediately:
  ```
  pip install --upgrade "ogham-mcp>=0.11.1"
  ```
- Users do not need to rotate anything on their end. The leaked credentials were owned by the project maintainer, not by users.

## Credit

Discovered during an internal pre-release audit on 2026-04-24 while preparing v0.11.1.

## References
- https://github.com/ogham-mcp/ogham-mcp/security/advisories/GHSA-8pqq-224h-x875
- https://github.com/ogham-mcp/ogham-mcp
