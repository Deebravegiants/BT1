# [H] Integer overflow in math ops in TensorFlow

## Summary
Severity: High
Advisory: BIT-tensorflow-2022-36015
Aliases: CVE-2022-36015, GHSA-rh87-q4vg-m45j, PYSEC-2026-1033, PYSEC-2026-3237, PYSEC-2026-3367
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2022-36015
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.9.0 <2.9.1

## Details
TensorFlow is an open source platform for machine learning. When `RangeSize` receives values that do not fit into an `int64_t`, it crashes. We have patched the issue in GitHub commit 37e64539cd29fcfb814c4451152a60f5d107b0f0. The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range. There are no known workarounds for this issue.

## References
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/ops/math_ops.cc
- https://github.com/tensorflow/tensorflow/commit/37e64539cd29fcfb814c4451152a60f5d107b0f0
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rh87-q4vg-m45j
- https://nvd.nist.gov/vuln/detail/CVE-2022-36015
