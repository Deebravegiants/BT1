# [H] Heap buffer overflow and undefined behavior in `FusedBatchNorm`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29583
Aliases: CVE-2021-29583, GHSA-9xh4-23q4-v6wr, PYSEC-2021-220, PYSEC-2021-511, PYSEC-2021-709
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29583
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.FusedBatchNorm` is vulnerable to a heap buffer overflow. If the tensors are empty, the same implementation can trigger undefined behavior by dereferencing null pointers. The implementation(https://github.com/tensorflow/tensorflow/blob/57d86e0db5d1365f19adcce848dfc1bf89fdd4c7/tensorflow/core/kernels/fused_batch_norm_op.cc) fails to validate that `scale`, `offset`, `mean` and `variance` (the last two only when required) all have the same number of elements as the number of channels of `x`. This results in heap out of bounds reads when the buffers backing these tensors are indexed past their boundary. If the tensors are empty, the validation mentioned in the above paragraph would also trigger and prevent the undefined behavior. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/6972f9dfe325636b3db4e0bc517ee22a159365c0
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9xh4-23q4-v6wr
- https://nvd.nist.gov/vuln/detail/CVE-2021-29583
