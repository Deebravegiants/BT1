# [M] Crash in `tf.transpose` with complex inputs

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29618
Aliases: CVE-2021-29618, GHSA-xqfj-cr6q-pc8w, PYSEC-2021-255, PYSEC-2021-546, PYSEC-2021-744
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29618
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Passing a complex argument to `tf.transpose` at the same time as passing `conjugate=True` argument results in a crash. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/issues/42105
- https://github.com/tensorflow/issues/46973
- https://github.com/tensorflow/tensorflow/commit/1dc6a7ce6e0b3e27a7ae650bfc05b195ca793f88
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xqfj-cr6q-pc8w
- https://nvd.nist.gov/vuln/detail/CVE-2021-29618
