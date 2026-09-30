# [M] Division by 0 in `QuantizedAdd`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29549
Aliases: CVE-2021-29549, GHSA-x83m-p7pv-ch8v, PYSEC-2021-186, PYSEC-2021-477, PYSEC-2021-675
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29549
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a runtime division by zero error and denial of service in `tf.raw_ops.QuantizedBatchNormWithGlobalNormalization`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/6f26b3f3418201479c264f2a02000880d8df151c/tensorflow/core/kernels/quantized_add_op.cc#L289-L295) computes a modulo operation without validating that the divisor is not zero. Since `vector_num_elements` is determined based on input shapes(https://github.com/tensorflow/tensorflow/blob/6f26b3f3418201479c264f2a02000880d8df151c/tensorflow/core/kernels/quantized_add_op.cc#L522-L544), a user can trigger scenarios where this quantity is 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/744009c9e5cc5d0447f0dc39d055f917e1fd9e16
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x83m-p7pv-ch8v
- https://nvd.nist.gov/vuln/detail/CVE-2021-29549
