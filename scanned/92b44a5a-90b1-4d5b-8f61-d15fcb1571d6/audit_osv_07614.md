# [M] CHECK-fail in `QuantizeAndDequantizeV4Grad`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29544
Aliases: CVE-2021-29544, GHSA-6g85-3hm8-83f9, PYSEC-2021-181, PYSEC-2021-472, PYSEC-2021-670
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29544
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a denial of service via a `CHECK`-fail in `tf.raw_ops.QuantizeAndDequantizeV4Grad`. This is because the implementation does not validate the rank of the `input_*` tensors. In turn, this results in the tensors being passes as they are to `QuantizeAndDequantizePerChannelGradientImpl`. However, the `vec<T>` method, requires the rank to 1 and triggers a `CHECK` failure otherwise. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2 as this is the only other affected version.

## References
- https://github.com/tensorflow/tensorflow/commit/20431e9044cf2ad3c0323c34888b192f3289af6b
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6g85-3hm8-83f9
- https://github.com/tensorflow/tensorflow/blob/95078c145b5a7a43ee046144005f733092756ab5/tensorflow/core/kernels/quantize_and_dequantize_op.cc#L162-L163
- https://github.com/tensorflow/tensorflow/blob/95078c145b5a7a43ee046144005f733092756ab5/tensorflow/core/kernels/quantize_and_dequantize_op.h#L295-L306
- https://nvd.nist.gov/vuln/detail/CVE-2021-29544
