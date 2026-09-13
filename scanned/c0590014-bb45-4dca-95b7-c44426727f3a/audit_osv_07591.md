# [M] Segfault in SparseCountSparseOutput

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29521
Aliases: CVE-2021-29521, GHSA-hr84-fqvp-48mm, PYSEC-2021-158, PYSEC-2021-449, PYSEC-2021-647
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29521
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Specifying a negative dense shape in `tf.raw_ops.SparseCountSparseOutput` results in a segmentation fault being thrown out from the standard library as `std::vector` invariants are broken. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/8f7b60ee8c0206a2c99802e3a4d1bb55d2bc0624/tensorflow/core/kernels/count_ops.cc#L199-L213) assumes the first element of the dense shape is always positive and uses it to initialize a `BatchedMap<T>` (i.e., `std::vector<absl::flat_hash_map<int64,T>>`(https://github.com/tensorflow/tensorflow/blob/8f7b60ee8c0206a2c99802e3a4d1bb55d2bc0624/tensorflow/core/kernels/count_ops.cc#L27)) data structure. If the `shape` tensor has more than one element, `num_batches` is the first value in `shape`. Ensuring that the `dense_shape` argument is a valid tensor shape (that is, all elements are non-negative) solves this issue. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2 and TensorFlow 2.3.3.

## References
- https://github.com/tensorflow/tensorflow/commit/c57c0b9f3a4f8684f3489dd9a9ec627ad8b599f5
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hr84-fqvp-48mm
- https://nvd.nist.gov/vuln/detail/CVE-2021-29521
