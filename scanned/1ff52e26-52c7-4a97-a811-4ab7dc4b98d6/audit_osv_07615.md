# [M] Heap buffer overflow in `SparseTensorToCSRSparseMatrix`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29545
Aliases: CVE-2021-29545, GHSA-hmg3-c7xj-6qwm, PYSEC-2021-182, PYSEC-2021-473, PYSEC-2021-671
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29545
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a denial of service via a `CHECK`-fail in converting sparse tensors to CSR Sparse matrices. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/800346f2c03a27e182dd4fba48295f65e7790739/tensorflow/core/kernels/sparse/kernels.cc#L66) does a double redirection to access an element of an array allocated on the heap. If the value at `indices(i, 0)` is such that `indices(i, 0) + 1` is outside the bounds of `csr_row_ptr`, this results in writing outside of bounds of heap allocated data. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/1e922ccdf6bf46a3a52641f99fd47d54c1decd13
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hmg3-c7xj-6qwm
- https://nvd.nist.gov/vuln/detail/CVE-2021-29545
