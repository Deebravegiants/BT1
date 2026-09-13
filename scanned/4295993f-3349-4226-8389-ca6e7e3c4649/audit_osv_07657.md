# [H] Division by zero in TFLite's implementation of `TransposeConv`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29588
Aliases: CVE-2021-29588, GHSA-vfr4-x8j2-3rf9, PYSEC-2021-225, PYSEC-2021-516, PYSEC-2021-714
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29588
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The optimized implementation of the `TransposeConv` TFLite operator is [vulnerable to a division by zero error](https://github.com/tensorflow/tensorflow/blob/0d45ea1ca641b21b73bcf9c00e0179cda284e7e7/tensorflow/lite/kernels/internal/optimized/optimized_ops.h#L5221-L5222). An attacker can craft a model such that `stride_{h,w}` values are 0. Code calling this function must validate these arguments. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/801c1c6be5324219689c98e1bd3e0ca365ee834d
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vfr4-x8j2-3rf9
- https://nvd.nist.gov/vuln/detail/CVE-2021-29588
