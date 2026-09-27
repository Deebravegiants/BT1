# [M] OOB read in `MatrixTriangularSolve`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29551
Aliases: CVE-2021-29551, GHSA-vqw6-72r7-fgw7, PYSEC-2021-188, PYSEC-2021-479, PYSEC-2021-677
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29551
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `MatrixTriangularSolve`(https://github.com/tensorflow/tensorflow/blob/8cae746d8449c7dda5298327353d68613f16e798/tensorflow/core/kernels/linalg/matrix_triangular_solve_op_impl.h#L160-L240) fails to terminate kernel execution if one validation condition fails. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/480641e3599775a8895254ffbc0fc45621334f68
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vqw6-72r7-fgw7
- https://nvd.nist.gov/vuln/detail/CVE-2021-29551
