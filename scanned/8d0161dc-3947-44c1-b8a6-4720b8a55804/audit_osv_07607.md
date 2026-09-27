# [H] Heap buffer overflow in `QuantizedResizeBilinear`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29537
Aliases: CVE-2021-29537, GHSA-8c89-2vwr-chcq, PYSEC-2021-174, PYSEC-2021-465, PYSEC-2021-663
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29537
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a heap buffer overflow in `QuantizedResizeBilinear` by passing in invalid thresholds for the quantization. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/50711818d2e61ccce012591eeb4fdf93a8496726/tensorflow/core/kernels/quantized_resize_bilinear_op.cc#L705-L706) assumes that the 2 arguments are always valid scalars and tries to access the numeric value directly. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/f6c40f0c6cbf00d46c7717a26419f2062f2f8694
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8c89-2vwr-chcq
- https://nvd.nist.gov/vuln/detail/CVE-2021-29537
