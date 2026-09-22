# [H] Reference binding to null pointer in `MatrixDiag*` ops

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29515
Aliases: CVE-2021-29515, GHSA-hc6c-75p4-hmq4, PYSEC-2021-152, PYSEC-2021-443, PYSEC-2021-641
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29515
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `MatrixDiag*` operations(https://github.com/tensorflow/tensorflow/blob/4c4f420e68f1cfaf8f4b6e8e3eb857e9e4c3ff33/tensorflow/core/kernels/linalg/matrix_diag_op.cc#L195-L197) does not validate that the tensor arguments are non-empty. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/a7116dd3913c4a4afd2a3a938573aa7c785fdfc6
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hc6c-75p4-hmq4
- https://nvd.nist.gov/vuln/detail/CVE-2021-29515
