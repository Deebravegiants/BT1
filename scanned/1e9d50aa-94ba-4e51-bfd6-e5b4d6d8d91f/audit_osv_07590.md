# [H] Heap buffer overflow in `Conv3DBackprop*`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29520
Aliases: CVE-2021-29520, GHSA-wcv5-qrj6-9pfm, PYSEC-2021-157, PYSEC-2021-448, PYSEC-2021-646
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29520
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Missing validation between arguments to `tf.raw_ops.Conv3DBackprop*` operations can result in heap buffer overflows. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/4814fafb0ca6b5ab58a09411523b2193fed23fed/tensorflow/core/kernels/conv_grad_shape_utils.cc#L94-L153) assumes that the `input`, `filter_sizes` and `out_backprop` tensors have the same shape, as they are accessed in parallel. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/8f37b52e1320d8d72a9529b2468277791a261197
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wcv5-qrj6-9pfm
- https://nvd.nist.gov/vuln/detail/CVE-2021-29520
