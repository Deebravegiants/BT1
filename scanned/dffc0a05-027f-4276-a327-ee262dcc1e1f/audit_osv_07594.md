# [M] Division by 0 in `Conv2DBackpropFilter`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29524
Aliases: CVE-2021-29524, GHSA-r4pj-74mg-8868, PYSEC-2021-161, PYSEC-2021-452, PYSEC-2021-650
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29524
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a division by 0 in `tf.raw_ops.Conv2DBackpropFilter`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/496c2630e51c1a478f095b084329acedb253db6b/tensorflow/core/kernels/conv_grad_shape_utils.cc#L130) does a modulus operation where the divisor is controlled by the caller. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/fca9874a9b42a2134f907d2fb46ab774a831404a
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-r4pj-74mg-8868
- https://nvd.nist.gov/vuln/detail/CVE-2021-29524
