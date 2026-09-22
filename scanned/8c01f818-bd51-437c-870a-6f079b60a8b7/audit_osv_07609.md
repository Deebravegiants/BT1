# [M] Segfault in tf.raw_ops.ImmutableConst

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29539
Aliases: CVE-2021-29539, GHSA-g4h2-gqm3-c9wq, PYSEC-2021-176, PYSEC-2021-467, PYSEC-2021-665
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29539
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Calling `tf.raw_ops.ImmutableConst`(https://www.tensorflow.org/api_docs/python/tf/raw_ops/ImmutableConst) with a `dtype` of `tf.resource` or `tf.variant` results in a segfault in the implementation as code assumes that the tensor contents are pure scalars. We have patched the issue in 4f663d4b8f0bec1b48da6fa091a7d29609980fa4 and will release TensorFlow 2.5.0 containing the patch. TensorFlow nightly packages after this commit will also have the issue resolved. If using `tf.raw_ops.ImmutableConst` in code, you can prevent the segfault by inserting a filter for the `dtype` argument.

## References
- https://github.com/tensorflow/tensorflow/commit/4f663d4b8f0bec1b48da6fa091a7d29609980fa4
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-g4h2-gqm3-c9wq
- https://nvd.nist.gov/vuln/detail/CVE-2021-29539
