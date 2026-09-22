# [M] CHECK-fail in AddManySparseToTensorsMap

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29523
Aliases: CVE-2021-29523, GHSA-2cpx-427x-q2c6, PYSEC-2021-160, PYSEC-2021-451, PYSEC-2021-649
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29523
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a denial of service via a `CHECK`-fail in `tf.raw_ops.AddManySparseToTensorsMap`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/6f9896890c4c703ae0a0845394086e2e1e523299/tensorflow/core/kernels/sparse_tensors_map_ops.cc#L257) takes the values specified in `sparse_shape` as dimensions for the output shape. The `TensorShape` constructor(https://github.com/tensorflow/tensorflow/blob/6f9896890c4c703ae0a0845394086e2e1e523299/tensorflow/core/framework/tensor_shape.cc#L183-L188) uses a `CHECK` operation which triggers when `InitDims`(https://github.com/tensorflow/tensorflow/blob/6f9896890c4c703ae0a0845394086e2e1e523299/tensorflow/core/framework/tensor_shape.cc#L212-L296) returns a non-OK status. This is a legacy implementation of the constructor and operations should use `BuildTensorShapeBase` or `AddDimWithStatus` to prevent `CHECK`-failures in the presence of overflows. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/69c68ecbb24dff3fa0e46da0d16c821a2dd22d7c
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-2cpx-427x-q2c6
- https://nvd.nist.gov/vuln/detail/CVE-2021-29523
