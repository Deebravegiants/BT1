# [H] Keras: Lambda deserialization can bypass safe mode and execute code

## Summary
Severity: High
Advisory: GHSA-5gwj-m78q-7pq3
CVE: CVE-2026-12481
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-03
Source: https://github.com/advisories/GHSA-5gwj-m78q-7pq3
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.12.3
- PyPI: `keras` — affected >=3.13.0 <3.15.0

## Details
A vulnerability in keras-team/keras version 3.14.0 allows for arbitrary code execution due to improper handling of deserialization in the `Lambda` layer. Specifically, the `_raise_for_lambda_deserialization()` function fails to enforce the safe-mode guard when `safe_mode` is set to `None`, which is the default value when `from_config()` is called outside of a `SafeModeScope` context. This logic error conflates `None` (unset/default-deny) with `False` (explicitly disabled), bypassing the guard and allowing attacker-controlled `marshal` bytecode to be deserialized. Affected call sites include `keras.layers.deserialize(config)`, `keras.models.clone_model(model)`, and any direct invocation of `Lambda.from_config(config)` without an enclosing `SafeModeScope(True)`. This vulnerability can be exploited to achieve arbitrary OS-level code execution in the context of the server or user process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-12481
- https://github.com/keras-team/keras/pull/23048
- https://github.com/keras-team/keras/pull/23165
- https://github.com/keras-team/keras/commit/55888d3becbdbb45dc16a55b489900f911e2dde5
- https://github.com/keras-team/keras/commit/d338a45204bdc787c8b3c4a9b82c1911cd52dedf
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.12.3
- https://github.com/keras-team/keras/releases/tag/v3.15.0
- https://huntr.com/bounties/59ceaed1-c8a3-4135-8f94-169ade02823d
