# [H] Division by 0 in `Conv2DBackpropInput`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29525
Aliases: CVE-2021-29525, GHSA-xm2v-8rrw-w9pm, PYSEC-2021-162, PYSEC-2021-453, PYSEC-2021-651
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29525
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a division by 0 in `tf.raw_ops.Conv2DBackpropInput`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/b40060c9f697b044e3107917c797ba052f4506ab/tensorflow/core/kernels/conv_grad_input_ops.h#L625-L655) does a division by a quantity that is controlled by the caller. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/2be2cdf3a123e231b16f766aa0e27d56b4606535
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xm2v-8rrw-w9pm
- https://nvd.nist.gov/vuln/detail/CVE-2021-29525
