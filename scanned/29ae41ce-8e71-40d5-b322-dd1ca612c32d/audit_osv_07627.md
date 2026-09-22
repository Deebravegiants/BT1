# [M] Division by 0 in `SparseMatMul`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29557
Aliases: CVE-2021-29557, GHSA-xw93-v57j-fcgh, PYSEC-2021-194, PYSEC-2021-485, PYSEC-2021-683
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29557
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a denial of service via a FPE runtime error in `tf.raw_ops.SparseMatMul`. The division by 0 occurs deep in Eigen code because the `b` tensor is empty. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/7f283ff806b2031f407db64c4d3edcda8fb9f9f5
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xw93-v57j-fcgh
- https://nvd.nist.gov/vuln/detail/CVE-2021-29557
