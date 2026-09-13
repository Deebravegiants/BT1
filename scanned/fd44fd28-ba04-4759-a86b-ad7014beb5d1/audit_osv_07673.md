# [M] Stack overflow in `ParseAttrValue` with nested tensors

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29615
Aliases: CVE-2021-29615, GHSA-qw5h-7f53-xrp6, PYSEC-2021-252, PYSEC-2021-543, PYSEC-2021-741
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29615
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `ParseAttrValue`(https://github.com/tensorflow/tensorflow/blob/c22d88d6ff33031aa113e48aa3fc9aa74ed79595/tensorflow/core/framework/attr_value_util.cc#L397-L453) can be tricked into stack overflow due to recursion by giving in a specially crafted input. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/e07e1c3d26492c06f078c7e5bf2d138043e199c1
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qw5h-7f53-xrp6
- https://nvd.nist.gov/vuln/detail/CVE-2021-29615
