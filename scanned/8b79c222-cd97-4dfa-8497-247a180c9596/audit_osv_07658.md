# [H] Division by zero in TFLite's implementation of `GatherNd`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29589
Aliases: CVE-2021-29589, GHSA-3w67-q784-6w7c, PYSEC-2021-226, PYSEC-2021-517, PYSEC-2021-715
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29589
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The reference implementation of the `GatherNd` TFLite operator is vulnerable to a division by zero error(https://github.com/tensorflow/tensorflow/blob/0d45ea1ca641b21b73bcf9c00e0179cda284e7e7/tensorflow/lite/kernels/internal/reference/reference_ops.h#L966). An attacker can craft a model such that `params` input would be an empty tensor. In turn, `params_shape.Dims(.)` would be zero, in at least one dimension. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/8e45822aa0b9f5df4b4c64f221e64dc930a70a9d
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-3w67-q784-6w7c
- https://nvd.nist.gov/vuln/detail/CVE-2021-29589
