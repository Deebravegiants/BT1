# [H] Heap buffer overflow in `MaxPool3DGradGrad`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29576
Aliases: CVE-2021-29576, GHSA-7cqx-92hp-x6wh, PYSEC-2021-213, PYSEC-2021-504, PYSEC-2021-702
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29576
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.MaxPool3DGradGrad` is vulnerable to a heap buffer overflow. The implementation(https://github.com/tensorflow/tensorflow/blob/596c05a159b6fbb9e39ca10b3f7753b7244fa1e9/tensorflow/core/kernels/pooling_ops_3d.cc#L694-L696) does not check that the initialization of `Pool3dParameters` completes successfully. Since the constructor(https://github.com/tensorflow/tensorflow/blob/596c05a159b6fbb9e39ca10b3f7753b7244fa1e9/tensorflow/core/kernels/pooling_ops_3d.cc#L48-L88) uses `OP_REQUIRES` to validate conditions, the first assertion that fails interrupts the initialization of `params`, making it contain invalid data. In turn, this might cause a heap buffer overflow, depending on default initialized values. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/63c6a29d0f2d692b247f7bf81f8732d6442fad09
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7cqx-92hp-x6wh
- https://nvd.nist.gov/vuln/detail/CVE-2021-29576
