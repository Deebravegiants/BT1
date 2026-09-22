# [M] Division by 0 in `QuantizedConv2D`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29527
Aliases: CVE-2021-29527, GHSA-x4g7-fvjj-prg8, PYSEC-2021-164, PYSEC-2021-455, PYSEC-2021-653
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29527
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a division by 0 in `tf.raw_ops.QuantizedConv2D`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/00e9a4d67d76703fa1aee33dac582acf317e0e81/tensorflow/core/kernels/quantized_conv_ops.cc#L257-L259) does a division by a quantity that is controlled by the caller. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/cfa91be9863a91d5105a3b4941096044ab32036b
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x4g7-fvjj-prg8
- https://nvd.nist.gov/vuln/detail/CVE-2021-29527
