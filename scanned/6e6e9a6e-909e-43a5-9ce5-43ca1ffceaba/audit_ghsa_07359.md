# [H] Keras: TorchModuleWrapper can deserialize unsafe PyTorch pickle data

## Summary
Severity: High
Advisory: GHSA-v2w2-w228-c444
CVE: CVE-2026-12484
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-19
Source: https://github.com/advisories/GHSA-v2w2-w228-c444
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.12.3
- PyPI: `keras` — affected >=3.13.0 <3.15.0

## Details
A vulnerability in keras-team/keras version 3.15.0 allows unsafe deserialization of attacker-controlled PyTorch pickle data through the public `keras.layers.TorchModuleWrapper.from_config` method. This method invokes `torch.load(..., weights_only=False)` without requiring an explicit unsafe opt-in, such as a `safe_mode=False` parameter. When called outside a `SafeModeScope(True)` context, the absence of an ambient safe mode state permits unsafe deserialization by default. This issue can lead to arbitrary code execution if untrusted Keras layer configurations are processed using this method. The vulnerability arises because the method does not enforce safe deserialization practices unless explicitly guarded by Keras safe mode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-12484
- https://github.com/keras-team/keras/pull/23048
- https://github.com/keras-team/keras/pull/23165
- https://github.com/keras-team/keras/commit/55888d3becbdbb45dc16a55b489900f911e2dde5
- https://github.com/keras-team/keras/commit/d338a45204bdc787c8b3c4a9b82c1911cd52dedf
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.12.3
- https://github.com/keras-team/keras/releases/tag/v3.15.0
- https://huntr.com/bounties/ab14df49-13b5-4442-b754-3189430bfa28
