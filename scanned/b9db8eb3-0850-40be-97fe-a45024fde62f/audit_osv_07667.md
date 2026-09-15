# [M] Division by zero in TFLite's implementation of `DepthwiseConv`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29602
Aliases: CVE-2021-29602, GHSA-rf3h-xgv5-2q39, PYSEC-2021-239, PYSEC-2021-530, PYSEC-2021-728
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29602
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of the `DepthwiseConv` TFLite operator is vulnerable to a division by zero error(https://github.com/tensorflow/tensorflow/blob/1a8e885b864c818198a5b2c0cbbeca5a1e833bc8/tensorflow/lite/kernels/depthwise_conv.cc#L287-L288). An attacker can craft a model such that `input`'s fourth dimension would be 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/cbda3c6b2dbbd3fbdc482ff8c0170a78ec2e97d0
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rf3h-xgv5-2q39
- https://nvd.nist.gov/vuln/detail/CVE-2021-29602
