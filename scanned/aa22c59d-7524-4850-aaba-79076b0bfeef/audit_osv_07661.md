# [H] Division by zero in TFLite's implementation of `DepthToSpace`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29595
Aliases: CVE-2021-29595, GHSA-vf94-36g5-69v8, PYSEC-2021-232, PYSEC-2021-523, PYSEC-2021-721
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29595
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of the `DepthToSpace` TFLite operator is vulnerable to a division by zero error(https://github.com/tensorflow/tensorflow/blob/0d45ea1ca641b21b73bcf9c00e0179cda284e7e7/tensorflow/lite/kernels/depth_to_space.cc#L63-L69). An attacker can craft a model such that `params->block_size` is 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/106d8f4fb89335a2c52d7c895b7a7485465ca8d9
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vf94-36g5-69v8
- https://nvd.nist.gov/vuln/detail/CVE-2021-29595
