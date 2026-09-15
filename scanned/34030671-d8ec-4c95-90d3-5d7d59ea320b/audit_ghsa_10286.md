# [H] Keras has an untrusted deserialization vulnerability

## Summary
Severity: High
Advisory: GHSA-4f3f-g24h-fr8m
CVE: CVE-2026-1462
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-4f3f-g24h-fr8m
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.13.2

## Details
A vulnerability in the `TFSMLayer` class of the `keras` package, version 3.13.0, allows attacker-controlled TensorFlow SavedModels to be loaded during deserialization of `.keras` models, even when `safe_mode=True`. This bypasses the security guarantees of `safe_mode` and enables arbitrary attacker-controlled code execution during model inference under the victim's privileges. The issue arises due to the unconditional loading of external SavedModels, serialization of attacker-controlled file paths, and the lack of validation in the `from_config()` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1462
- https://github.com/keras-team/keras/pull/22035
- https://github.com/keras-team/keras/commit/b6773d3decaef1b05d8e794458e148cb362f163f
- https://github.com/keras-team/keras
- https://huntr.com/bounties/7e78d6f1-6977-4300-b595-e81bdbda331c
