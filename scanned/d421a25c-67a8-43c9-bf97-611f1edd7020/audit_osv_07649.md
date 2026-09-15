# [M] Undefined behavior and `CHECK`-fail in `FractionalMaxPoolGrad`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29580
Aliases: CVE-2021-29580, GHSA-x8h6-xgqx-jqgp, PYSEC-2021-217, PYSEC-2021-508, PYSEC-2021-706
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29580
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.FractionalMaxPoolGrad` triggers an undefined behavior if one of the input tensors is empty. The code is also vulnerable to a denial of service attack as a `CHECK` condition becomes false and aborts the process. The implementation(https://github.com/tensorflow/tensorflow/blob/169054888d50ce488dfde9ca55d91d6325efbd5b/tensorflow/core/kernels/fractional_max_pool_op.cc#L215) fails to validate that input and output tensors are not empty and are of the same rank. Each of these unchecked assumptions is responsible for the above issues. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/32fdcbff9d06d010d908fcc4bd4b36eb3ce15925
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x8h6-xgqx-jqgp
- https://nvd.nist.gov/vuln/detail/CVE-2021-29580
