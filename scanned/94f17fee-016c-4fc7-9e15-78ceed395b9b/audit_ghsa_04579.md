# [M] vLLM: temperature=NaN and temperature=Infinity bypass validation and propagate to GPU kernels

## Summary
Severity: Medium
Advisory: GHSA-7h4p-rffg-7823
CVE: CVE-2026-54235
CWE: CWE-1287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-7h4p-rffg-7823
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.8.5 <0.24.0

## Details
## Summary

All temperature validation gates use comparison operators (`<`, `>`), which silently evaluate to `False` for `NaN` and for positive `Infinity` in Python's IEEE 754 float semantics. Both values pass every guard and propagate to GPU sampling kernels, where they produce undefined behavior or CUDA errors that can crash the inference worker. Note: `-Infinity` is correctly caught.

## Root Cause

`sampling_params.py:384`:
```python
if 0 < self.temperature < _MAX_TEMP:  # NaN → False; +Inf → False
```

`sampling_params.py:462`:
```python
if self.temperature < 0.0:            # NaN → False; +Inf → False
    raise VLLMValidationError(...)
```

No `math.isnan()` or `math.isinf()` check exists anywhere in `sampling_params.py`.

Python semantics (verified): `float('nan') < 0.0` → `False`, `float('inf') < 0.0` → `False`.


## Impact

Crash of inference worker on GPU kernel execution with NaN/Inf softmax input, degrading service for all concurrent users.

## Remediation

Add `math.isfinite(self.temperature)` check in `_verify_args()`. Reject non-finite float values with a 400 error.

## Fix

A fix for this vulnerability was merged here: https://github.com/vllm-project/vllm/pull/45116

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-7h4p-rffg-7823
- https://nvd.nist.gov/vuln/detail/CVE-2026-54235
- https://github.com/vllm-project/vllm/pull/45116
- https://github.com/vllm-project/vllm/commit/d598d239737cfa37bcfcb98886ec3f3557fc7198
- https://github.com/advisories/GHSA-7h4p-rffg-7823
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-3405.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
