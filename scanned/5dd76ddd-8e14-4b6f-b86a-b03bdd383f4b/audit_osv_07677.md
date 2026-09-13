# [M] Segfault in `tf.raw_ops.SparseCountSparseOutput`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29619
Aliases: CVE-2021-29619, GHSA-wvjw-p9f5-vq28, PYSEC-2021-256, PYSEC-2021-547, PYSEC-2021-745
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29619
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Passing invalid arguments (e.g., discovered via fuzzing) to `tf.raw_ops.SparseCountSparseOutput` results in segfault. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/82e6203221865de4008445b13c69b6826d2b28d9
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wvjw-p9f5-vq28
- https://nvd.nist.gov/vuln/detail/CVE-2021-29619
