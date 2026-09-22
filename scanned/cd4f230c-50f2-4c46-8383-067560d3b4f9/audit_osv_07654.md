# [H] Division by zero in padding computation in TFLite

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29585
Aliases: CVE-2021-29585, GHSA-mv78-g7wq-mhp4, PYSEC-2021-222, PYSEC-2021-513, PYSEC-2021-711
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29585
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The TFLite computation for size of output after padding, `ComputeOutSize`(https://github.com/tensorflow/tensorflow/blob/0c9692ae7b1671c983569e5d3de5565843d500cf/tensorflow/lite/kernels/padding.h#L43-L55), does not check that the `stride` argument is not 0 before doing the division. Users can craft special models such that `ComputeOutSize` is called with `stride` set to 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/49847ae69a4e1a97ae7f2db5e217c77721e37948
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mv78-g7wq-mhp4
- https://nvd.nist.gov/vuln/detail/CVE-2021-29585
