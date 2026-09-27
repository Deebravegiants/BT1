# [M] Division by 0 in `Conv2D`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29526
Aliases: CVE-2021-29526, GHSA-4vf2-4xcg-65cx, PYSEC-2021-163, PYSEC-2021-454, PYSEC-2021-652
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29526
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a division by 0 in `tf.raw_ops.Conv2D`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/988087bd83f144af14087fe4fecee2d250d93737/tensorflow/core/kernels/conv_ops.cc#L261-L263) does a division by a quantity that is controlled by the caller. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/b12aa1d44352de21d1a6faaf04172d8c2508b42b
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4vf2-4xcg-65cx
- https://nvd.nist.gov/vuln/detail/CVE-2021-29526
