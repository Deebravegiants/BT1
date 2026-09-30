# [M] CHECK-fail in `tf.raw_ops.IRFFT`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29562
Aliases: CVE-2021-29562, GHSA-36vm-xw34-x4pj, PYSEC-2021-199, PYSEC-2021-490, PYSEC-2021-688
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29562
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a denial of service by exploiting a `CHECK`-failure coming from the implementation of `tf.raw_ops.IRFFT`. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/1c56f53be0b722ca657cbc7df461ed676c8642a2
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-36vm-xw34-x4pj
- https://nvd.nist.gov/vuln/detail/CVE-2021-29562
