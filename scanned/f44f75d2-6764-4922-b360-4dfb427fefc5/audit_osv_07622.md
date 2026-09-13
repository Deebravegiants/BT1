# [M] CHECK-failure in `UnsortedSegmentJoin`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29552
Aliases: CVE-2021-29552, GHSA-jhq9-wm9m-cf89, PYSEC-2021-189, PYSEC-2021-480, PYSEC-2021-678
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29552
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a denial of service by controlling the values of `num_segments` tensor argument for `UnsortedSegmentJoin`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/a2a607db15c7cd01d754d37e5448d72a13491bdb/tensorflow/core/kernels/unsorted_segment_join_op.cc#L92-L93) assumes that the `num_segments` tensor is a valid scalar. Since the tensor is empty the `CHECK` involved in `.scalar<T>()()` that checks that the number of elements is exactly 1 will be invalidated and this would result in process termination. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/704866eabe03a9aeda044ec91a8d0c83fc1ebdbe
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-jhq9-wm9m-cf89
- https://nvd.nist.gov/vuln/detail/CVE-2021-29552
