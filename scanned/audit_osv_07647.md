# [H] Heap buffer overflow in `AvgPool3DGrad`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29577
Aliases: CVE-2021-29577, GHSA-v6r6-84gr-92rm, PYSEC-2021-214, PYSEC-2021-505, PYSEC-2021-703
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29577
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.AvgPool3DGrad` is vulnerable to a heap buffer overflow. The implementation(https://github.com/tensorflow/tensorflow/blob/d80ffba9702dc19d1fac74fc4b766b3fa1ee976b/tensorflow/core/kernels/pooling_ops_3d.cc#L376-L450) assumes that the `orig_input_shape` and `grad` tensors have similar first and last dimensions but does not check that this assumption is validated. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/6fc9141f42f6a72180ecd24021c3e6b36165fe0d
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-v6r6-84gr-92rm
- https://nvd.nist.gov/vuln/detail/CVE-2021-29577
