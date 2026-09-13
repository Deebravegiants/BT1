# [H] Invalid validation in `SparseMatrixSparseCholesky`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29530
Aliases: CVE-2021-29530, GHSA-xcwj-wfcm-m23c, PYSEC-2021-167, PYSEC-2021-458, PYSEC-2021-656
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29530
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a null pointer dereference by providing an invalid `permutation` to `tf.raw_ops.SparseMatrixSparseCholesky`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/080f1d9e257589f78b3ffb75debf584168aa6062/tensorflow/core/kernels/sparse/sparse_cholesky_op.cc#L85-L86) fails to properly validate the input arguments. Although `ValidateInputs` is called and there are checks in the body of this function, the code proceeds to the next line in `ValidateInputs` since `OP_REQUIRES`(https://github.com/tensorflow/tensorflow/blob/080f1d9e257589f78b3ffb75debf584168aa6062/tensorflow/core/framework/op_requires.h#L41-L48) is a macro that only exits the current function. Thus, the first validation condition that fails in `ValidateInputs` will cause an early return from that function. However, the caller will continue execution from the next line. The fix is to either explicitly check `context->status()` or to convert `ValidateInputs` to return a `Status`. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/e6a7c7cc18c3aaad1ae0872cb0a959f5c923d2bd
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xcwj-wfcm-m23c
- https://nvd.nist.gov/vuln/detail/CVE-2021-29530
