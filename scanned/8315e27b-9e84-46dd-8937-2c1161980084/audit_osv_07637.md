# [M] Lack of validation in `SparseDenseCwiseMul`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29567
Aliases: CVE-2021-29567, GHSA-wp3c-xw9g-gpcg, PYSEC-2021-204, PYSEC-2021-495, PYSEC-2021-693
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29567
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Due to lack of validation in `tf.raw_ops.SparseDenseCwiseMul`, an attacker can trigger denial of service via `CHECK`-fails or accesses to outside the bounds of heap allocated data. Since the implementation(https://github.com/tensorflow/tensorflow/blob/38178a2f7a681a7835bb0912702a134bfe3b4d84/tensorflow/core/kernels/sparse_dense_binary_op_shared.cc#L68-L80) only validates the rank of the input arguments but no constraints between dimensions(https://www.tensorflow.org/api_docs/python/tf/raw_ops/SparseDenseCwiseMul), an attacker can abuse them to trigger internal `CHECK` assertions (and cause program termination, denial of service) or to write to memory outside of bounds of heap allocated tensor buffers. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/7ae2af34087fb4b5c8915279efd03da3b81028bc
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wp3c-xw9g-gpcg
- https://nvd.nist.gov/vuln/detail/CVE-2021-29567
