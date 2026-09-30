# [M] Division by 0 in `MaxPoolGradWithArgmax`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29573
Aliases: CVE-2021-29573, GHSA-9vpm-rcf4-9wqw, PYSEC-2021-210, PYSEC-2021-501, PYSEC-2021-699
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29573
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.MaxPoolGradWithArgmax` is vulnerable to a division by 0. The implementation(https://github.com/tensorflow/tensorflow/blob/279bab6efa22752a2827621b7edb56a730233bd8/tensorflow/core/kernels/maxpooling_op.cc#L1033-L1034) fails to validate that the batch dimension of the tensor is non-zero, before dividing by this quantity. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/376c352a37ce5a68b721406dc7e77ac4b6cf483d
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9vpm-rcf4-9wqw
- https://nvd.nist.gov/vuln/detail/CVE-2021-29573
