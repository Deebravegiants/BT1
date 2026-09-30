# [M] CHECK-fail in SparseCross due to type confusion

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29519
Aliases: CVE-2021-29519, GHSA-772j-h9xw-ffp5, PYSEC-2021-156, PYSEC-2021-447, PYSEC-2021-645
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29519
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The API of `tf.raw_ops.SparseCross` allows combinations which would result in a `CHECK`-failure and denial of service. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/3d782b7d47b1bf2ed32bd4a246d6d6cadc4c903d/tensorflow/core/kernels/sparse_cross_op.cc#L114-L116) is tricked to consider a tensor of type `tstring` which in fact contains integral elements. Fixing the type confusion by preventing mixing `DT_STRING` and `DT_INT64` types solves this issue. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/b1cc5e5a50e7cee09f2c6eb48eb40ee9c4125025
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-772j-h9xw-ffp5
- https://nvd.nist.gov/vuln/detail/CVE-2021-29519
