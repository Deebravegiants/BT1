# [M] check-jsonschema default caching for remote schemas allows for cache confusion

## Summary
Severity: Medium
Advisory: GHSA-q6mv-284r-mp36
CVE: CVE-2024-53848
CWE: CWE-349
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-q6mv-284r-mp36
Type: github-advisory

## Affected
- PyPI: `check-jsonschema` — affected >=0 <0.30.0

## Details
### Impact

The default cache strategy uses the basename of a remote schema as the name of the file in the cache, e.g. `https://example.org/schema.json` will be stored as `schema.json`. This naming allows for conflicts. If an attacker can get a user to run `check-jsonschema` against a malicious schema URL, e.g., `https://example.evil.org/schema.json`, they can insert their own schema into the cache and it will be picked up and used instead of the appropriate schema.

Such a cache confusion attack could be used to allow data to pass validation which should have been rejected.

### Patches

A patch is in progress but has not yet been released.

### Workarounds

- Users can use `--no-cache` to disable caching.
- Users can use `--cache-filename` to select filenames for use in the cache, or to ensure that other usages do not overwrite the cached schema. (Note: this flag is being deprecated as part of the remediation effort.)
- Users can explicitly download the schema before use as a local file, as in `curl -LOs https://example.org/schema.json; check-jsonschema --schemafile ./schema.json`

## References
- https://github.com/python-jsonschema/check-jsonschema/security/advisories/GHSA-q6mv-284r-mp36
- https://nvd.nist.gov/vuln/detail/CVE-2024-53848
- https://github.com/python-jsonschema/check-jsonschema/commit/c52714b85e6725b1b24516fbdedacb333b939152
- https://github.com/python-jsonschema/check-jsonschema
