# [H] Heap OOB access in unicode ops

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29559
Aliases: CVE-2021-29559, GHSA-59q2-x2qc-4c97, PYSEC-2021-196, PYSEC-2021-487, PYSEC-2021-685
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29559
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can access data outside of bounds of heap allocated array in `tf.raw_ops.UnicodeEncode`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/472c1f12ad9063405737679d4f6bd43094e1d36d/tensorflow/core/kernels/unicode_ops.cc) assumes that the `input_value`/`input_splits` pair specify a valid sparse tensor. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/51300ba1cc2f487aefec6e6631fef03b0e08b298
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-59q2-x2qc-4c97
- https://nvd.nist.gov/vuln/detail/CVE-2021-29559
