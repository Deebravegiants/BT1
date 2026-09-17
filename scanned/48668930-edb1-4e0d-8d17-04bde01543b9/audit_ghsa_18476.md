# [H] Bugsink path traversal via event_id in ingestion

## Summary
Severity: High
Advisory: GHSA-q78p-g86f-jg6q
CVE: CVE-2025-54433
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-29
Source: https://github.com/advisories/GHSA-q78p-g86f-jg6q
Type: github-advisory

## Affected
- PyPI: `bugsink` — affected >=1.7.0 <1.7.4
- PyPI: `bugsink` — affected >=1.6.0 <1.6.4
- PyPI: `bugsink` — affected >=1.5.0 <1.5.5
- PyPI: `bugsink` — affected >=0 <1.4.3

## Details
## Summary

In affected versions, ingestion paths construct file locations directly from untrusted `event_id` input without validation. A specially crafted `event_id` can result in paths outside the intended directory, potentially allowing file overwrite or creation in arbitrary locations.

Submitting such input requires access to a valid DSN. While that limits exposure, DSNs are sometimes discoverable—for example, when included in frontend code—and should not be treated as a strong security boundary.

## Impact

A valid DSN holder can craft an `event_id` that causes the ingestion process to write files outside its designated directory. This allows overwriting files accessible to the user running Bugsink.

If Bugsink runs in a container, the effect is confined to the container’s filesystem. In non-containerized setups, the overwrite may affect other parts of the system accessible to that user.

## Mitigation

Update to version `1.7.4`, `1.6.4`, `1.5.5` or `1.4.3` , which require `event_id` to be a valid UUID and normalizes it before use in file paths.

## References
- https://github.com/bugsink/bugsink/security/advisories/GHSA-q78p-g86f-jg6q
- https://nvd.nist.gov/vuln/detail/CVE-2025-54433
- https://github.com/bugsink/bugsink/commit/1001726f4389e982c486cdd5fa81941cb46cfc33
- https://github.com/bugsink/bugsink/commit/211ddf76758c808c095b5f836c363f148d934d21
- https://github.com/bugsink/bugsink/commit/2c41fbe3881bdea83399a7f9fdc8cff198ae089f
- https://github.com/bugsink/bugsink/commit/53cf1a17a3e96f7c83c7451fd56f980a09d0c9b0
- https://github.com/bugsink/bugsink/commit/55a155003d0b416ea008c5e7dcde85130ad21d9b
- https://github.com/bugsink/bugsink/commit/b94aa8a5c96ce8cdd9711b6beb4e518264993ac2
- https://github.com/bugsink/bugsink/commit/c341687bd655543730c812db35c29199f788be6b
- https://github.com/bugsink/bugsink/commit/c87217bd565122ba70af90436e3ab2cd9bee658f
- https://github.com/bugsink/bugsink
