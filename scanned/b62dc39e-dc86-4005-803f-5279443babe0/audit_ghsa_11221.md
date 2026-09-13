# [M] openssl-encrypt silently skips schema validation when jsonschema library is not installed

## Summary
Severity: Medium
Advisory: GHSA-425g-fjhq-5h92
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-425g-fjhq-5h92
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
### Summary

In `openssl_encrypt/modules/json_validator.py` at **lines 234-238**, when the `jsonschema` library is not installed, all schema validation is silently skipped with only a print warning.

### Affected Code

```python
if not JSONSCHEMA_AVAILABLE:
    print(f"Warning: Cannot validate against schema '{schema_name}' - jsonschema library not available")
    return
```

Additionally, unknown metadata format versions (line 288-293) bypass schema validation entirely, and all schemas use `additionalProperties: true` allowing arbitrary extra fields.

### Impact

An attacker who can influence the Python environment (remove the jsonschema package) or craft metadata with an unknown version number can bypass all schema checks. Malformed or malicious metadata will be accepted without validation.

### Recommended Fix

- Make `jsonschema` a required dependency, not optional
- Or fail-closed: refuse to process metadata when validation cannot be performed
- Reject unknown format versions instead of silently skipping validation
- Consider using `additionalProperties: false` in schemas

### Fix

Fixed in commit `6e7f938` on branch `releases/1.4.x` — validate_against_schema() now raises JSONValidationError when jsonschema is unavailable instead of silently passing; changed print() warning to logging.warning().

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-425g-fjhq-5h92
- https://github.com/jahlives/openssl_encrypt/commit/6e7f938dcb7928faf5fd12bb5559f6dae2944124
- https://github.com/jahlives/openssl_encrypt
