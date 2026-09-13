# [M] CHECK-fail in `tf.raw_ops.RFFT`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29563
Aliases: CVE-2021-29563, GHSA-ph87-fvjr-v33w, PYSEC-2021-200, PYSEC-2021-491, PYSEC-2021-689
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29563
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a denial of service by exploiting a `CHECK`-failure coming from the implementation of `tf.raw_ops.RFFT`. Eigen code operating on an empty matrix can trigger on an assertion and will cause program termination. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/31bd5026304677faa8a0b77602c6154171b9aec1
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-ph87-fvjr-v33w
- https://nvd.nist.gov/vuln/detail/CVE-2021-29563
