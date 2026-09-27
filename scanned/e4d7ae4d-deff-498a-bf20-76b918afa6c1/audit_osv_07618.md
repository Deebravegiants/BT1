# [M] Division by 0 in `QuantizedBatchNormWithGlobalNormalization`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29548
Aliases: CVE-2021-29548, GHSA-p45v-v4pw-77jr, PYSEC-2021-185, PYSEC-2021-476, PYSEC-2021-674
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29548
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a runtime division by zero error and denial of service in `tf.raw_ops.QuantizedBatchNormWithGlobalNormalization`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/55a97caa9e99c7f37a0bbbeb414dc55553d3ae7f/tensorflow/core/kernels/quantized_batch_norm_op.cc) does not validate all constraints specified in the op's contract(https://www.tensorflow.org/api_docs/python/tf/raw_ops/QuantizedBatchNormWithGlobalNormalization). The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/d6ed5bcfe1dcab9e85a4d39931bd18d99018e75b
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p45v-v4pw-77jr
- https://nvd.nist.gov/vuln/detail/CVE-2021-29548
