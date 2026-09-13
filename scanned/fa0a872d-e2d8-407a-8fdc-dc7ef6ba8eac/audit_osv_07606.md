# [H] Heap buffer overflow in `QuantizedReshape`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29536
Aliases: CVE-2021-29536, GHSA-2gfx-95x2-5v3x, PYSEC-2021-173, PYSEC-2021-464, PYSEC-2021-662
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29536
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a heap buffer overflow in `QuantizedReshape` by passing in invalid thresholds for the quantization. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/a324ac84e573fba362a5e53d4e74d5de6729933e/tensorflow/core/kernels/quantized_reshape_op.cc#L38-L55) assumes that the 2 arguments are always valid scalars and tries to access the numeric value directly. However, if any of these tensors is empty, then `.flat<T>()` is an empty buffer and accessing the element at position 0 results in overflow. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/a324ac84e573fba362a5e53d4e74d5de6729933e
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-2gfx-95x2-5v3x
- https://nvd.nist.gov/vuln/detail/CVE-2021-29536
