# [H] Invalid validation in `QuantizeAndDequantizeV2`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29610
Aliases: CVE-2021-29610, GHSA-mq5c-prh3-3f3h, PYSEC-2021-247, PYSEC-2021-538, PYSEC-2021-736
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29610
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The validation in `tf.raw_ops.QuantizeAndDequantizeV2` allows invalid values for `axis` argument:. The validation(https://github.com/tensorflow/tensorflow/blob/eccb7ec454e6617738554a255d77f08e60ee0808/tensorflow/core/kernels/quantize_and_dequantize_op.cc#L74-L77) uses `||` to mix two different conditions. If `axis_ < -1` the condition in `OP_REQUIRES` will still be true, but this value of `axis_` results in heap underflow. This allows attackers to read/write to other data on the heap. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/c5b0d5f8ac19888e46ca14b0e27562e7fbbee9a9
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mq5c-prh3-3f3h
- https://nvd.nist.gov/vuln/detail/CVE-2021-29610
