# [H] Heap buffer overflow in `QuantizedMul`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29535
Aliases: CVE-2021-29535, GHSA-m3f9-w3p3-p669, PYSEC-2021-172, PYSEC-2021-463, PYSEC-2021-661
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29535
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a heap buffer overflow in `QuantizedMul` by passing in invalid thresholds for the quantization. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/87cf4d3ea9949051e50ca3f071fc909538a51cd0/tensorflow/core/kernels/quantized_mul_op.cc#L287-L290) assumes that the 4 arguments are always valid scalars and tries to access the numeric value directly. However, if any of these tensors is empty, then `.flat<T>()` is an empty buffer and accessing the element at position 0 results in overflow. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/efea03b38fb8d3b81762237dc85e579cc5fc6e87
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-m3f9-w3p3-p669
- https://nvd.nist.gov/vuln/detail/CVE-2021-29535
