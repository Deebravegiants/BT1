# [H] CVE-2021-29578

## Summary
Severity: High
Advisory: CVE-2021-29578
Aliases: BIT-tensorflow-2021-29578, GHSA-6f89-8j54-29xf, PYSEC-2021-215, PYSEC-2021-506, PYSEC-2021-704
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/CVE-2021-29578
Type: osv

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.FractionalAvgPoolGrad` is vulnerable to a heap buffer overflow. The implementation(https://github.com/tensorflow/tensorflow/blob/dcba796a28364d6d7f003f6fe733d82726dda713/tensorflow/core/kernels/fractional_avg_pool_op.cc#L216) fails to validate that the pooling sequence arguments have enough elements as required by the `out_backprop` tensor shape. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/12c727cee857fa19be717f336943d95fca4ffe4f
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6f89-8j54-29xf
