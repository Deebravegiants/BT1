# [H] Heap OOB read in `tf.raw_ops.Dequantize`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29582
Aliases: CVE-2021-29582, GHSA-c45w-2wxr-pp53, PYSEC-2021-219, PYSEC-2021-510, PYSEC-2021-708
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29582
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Due to lack of validation in `tf.raw_ops.Dequantize`, an attacker can trigger a read from outside of bounds of heap allocated data. The implementation(https://github.com/tensorflow/tensorflow/blob/26003593aa94b1742f34dc22ce88a1e17776a67d/tensorflow/core/kernels/dequantize_op.cc#L106-L131) accesses the `min_range` and `max_range` tensors in parallel but fails to check that they have the same shape. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/5899741d0421391ca878da47907b1452f06aaf1b
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-c45w-2wxr-pp53
- https://nvd.nist.gov/vuln/detail/CVE-2021-29582
