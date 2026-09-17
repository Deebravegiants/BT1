# [M] Null pointer dereference in `EditDistance`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29564
Aliases: CVE-2021-29564, GHSA-75f6-78jr-4656, PYSEC-2021-201, PYSEC-2021-492, PYSEC-2021-690
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29564
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a null pointer dereference in the implementation of `tf.raw_ops.EditDistance`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/79865b542f9ffdc9caeb255631f7c56f1d4b6517/tensorflow/core/kernels/edit_distance_op.cc#L103-L159) has incomplete validation of the input parameters. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/f4c364a5d6880557f6f5b6eb5cee2c407f0186b3
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-75f6-78jr-4656
- https://nvd.nist.gov/vuln/detail/CVE-2021-29564
