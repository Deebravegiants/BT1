# [H] Division by zero in TFLite's implementation of `SpaceToDepth`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29587
Aliases: CVE-2021-29587, GHSA-j7rm-8ww4-xx2g, PYSEC-2021-224, PYSEC-2021-515, PYSEC-2021-713
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29587
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The `Prepare` step of the `SpaceToDepth` TFLite operator does not check for 0 before division(https://github.com/tensorflow/tensorflow/blob/5f7975d09eac0f10ed8a17dbb6f5964977725adc/tensorflow/lite/kernels/space_to_depth.cc#L63-L67). An attacker can craft a model such that `params->block_size` would be zero. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/0d45ea1ca641b21b73bcf9c00e0179cda284e7e7
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-j7rm-8ww4-xx2g
- https://nvd.nist.gov/vuln/detail/CVE-2021-29587
