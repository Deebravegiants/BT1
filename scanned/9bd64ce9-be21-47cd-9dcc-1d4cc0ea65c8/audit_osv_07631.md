# [M] CHECK-fail in `LoadAndRemapMatrix`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29561
Aliases: CVE-2021-29561, GHSA-gvm4-h8j3-rjrq, PYSEC-2021-198, PYSEC-2021-489, PYSEC-2021-687
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29561
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a denial of service by exploiting a `CHECK`-failure coming from `tf.raw_ops.LoadAndRemapMatrix`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/d94227d43aa125ad8b54115c03cece54f6a1977b/tensorflow/core/kernels/ragged_tensor_to_tensor_op.cc#L219-L222) assumes that the `ckpt_path` is always a valid scalar. However, an attacker can send any other tensor as the first argument of `LoadAndRemapMatrix`. This would cause the rank `CHECK` in `scalar<T>()()` to trigger and terminate the process. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/77dd114513d7796e1e2b8aece214a380af26fbf4
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gvm4-h8j3-rjrq
- https://nvd.nist.gov/vuln/detail/CVE-2021-29561
