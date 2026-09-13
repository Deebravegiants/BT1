# [H] Heap buffer overflow in `SparseSplit`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29558
Aliases: CVE-2021-29558, GHSA-mqh2-9wrp-vx84, PYSEC-2021-195, PYSEC-2021-486, PYSEC-2021-684
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29558
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a heap buffer overflow in `tf.raw_ops.SparseSplit`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/699bff5d961f0abfde8fa3f876e6d241681fbef8/tensorflow/core/util/sparse/sparse_tensor.h#L528-L530) accesses an array element based on a user controlled offset. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/8ba6fa29cd8bf9cef9b718dc31c78c73081f5b31
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mqh2-9wrp-vx84
- https://nvd.nist.gov/vuln/detail/CVE-2021-29558
