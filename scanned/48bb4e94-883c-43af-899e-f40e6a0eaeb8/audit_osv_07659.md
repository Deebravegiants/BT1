# [H] Division by zero in TFLite's implementation of `BatchToSpaceNd`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29593
Aliases: CVE-2021-29593, GHSA-cfx7-2xpc-8w4h, PYSEC-2021-230, PYSEC-2021-521, PYSEC-2021-719
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29593
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of the `BatchToSpaceNd` TFLite operator is vulnerable to a division by zero error(https://github.com/tensorflow/tensorflow/blob/b5ed552fe55895aee8bd8b191f744a069957d18d/tensorflow/lite/kernels/batch_to_space_nd.cc#L81-L82). An attacker can craft a model such that one dimension of the `block` input is 0. Hence, the corresponding value in `block_shape` is 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/2c74674348a4708ced58ad6eb1b23354df8ee044
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cfx7-2xpc-8w4h
- https://nvd.nist.gov/vuln/detail/CVE-2021-29593
