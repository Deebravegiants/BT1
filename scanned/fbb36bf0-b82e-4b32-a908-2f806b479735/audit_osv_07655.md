# [H] Division by zero in optimized pooling implementations in TFLite

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29586
Aliases: CVE-2021-29586, GHSA-26j7-6w8w-7922, PYSEC-2021-223, PYSEC-2021-514, PYSEC-2021-712
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29586
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Optimized pooling implementations in TFLite fail to check that the stride arguments are not 0 before calling `ComputePaddingHeightWidth`(https://github.com/tensorflow/tensorflow/blob/3f24ccd932546416ec906a02ddd183b48a1d2c83/tensorflow/lite/kernels/pooling.cc#L90). Since users can craft special models which will have `params->stride_{height,width}` be zero, this will result in a division by zero. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/5f7975d09eac0f10ed8a17dbb6f5964977725adc
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-26j7-6w8w-7922
- https://nvd.nist.gov/vuln/detail/CVE-2021-29586
