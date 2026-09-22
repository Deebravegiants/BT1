# [M] Incomplete validation in `SparseReshape`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29611
Aliases: CVE-2021-29611, GHSA-9rpc-5v9q-5r7f, PYSEC-2021-248, PYSEC-2021-539, PYSEC-2021-737
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29611
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Incomplete validation in `SparseReshape` results in a denial of service based on a `CHECK`-failure. The implementation(https://github.com/tensorflow/tensorflow/blob/e87b51ce05c3eb172065a6ea5f48415854223285/tensorflow/core/kernels/sparse_reshape_op.cc#L40) has no validation that the input arguments specify a valid sparse tensor. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2 and TensorFlow 2.3.3, as these are the only affected versions.

## References
- https://github.com/tensorflow/tensorflow/commit/1d04d7d93f4ed3854abf75d6b712d72c3f70d6b6
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9rpc-5v9q-5r7f
- https://nvd.nist.gov/vuln/detail/CVE-2021-29611
