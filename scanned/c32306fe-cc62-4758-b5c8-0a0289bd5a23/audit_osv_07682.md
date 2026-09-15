# [H] `CHECK`-fail in `tensorflow::full_type::SubstituteFromAttrs` in TensorFlow

## Summary
Severity: High
Advisory: BIT-tensorflow-2022-36016
Aliases: CVE-2022-36016, GHSA-g468-qj8g-vcjc, PYSEC-2026-3184, PYSEC-2026-3327, PYSEC-2026-996
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2022-36016
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.9.0 <2.9.1

## Details
TensorFlow is an open source platform for machine learning. When `tensorflow::full_type::SubstituteFromAttrs` receives a `FullTypeDef& t` that is not exactly three args, it triggers a `CHECK`-fail instead of returning a status. We have patched the issue in GitHub commit 6104f0d4091c260ce9352f9155f7e9b725eab012. The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range. There are no known workarounds for this issue.

## References
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/ops/math_ops.cc
- https://github.com/tensorflow/tensorflow/commit/6104f0d4091c260ce9352f9155f7e9b725eab012
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-g468-qj8g-vcjc
- https://nvd.nist.gov/vuln/detail/CVE-2022-36016
