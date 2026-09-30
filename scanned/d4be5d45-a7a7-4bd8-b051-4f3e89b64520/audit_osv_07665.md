# [H] Division by zero in TFLite's implementation of `Split`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29599
Aliases: CVE-2021-29599, GHSA-97wf-p777-86jq, PYSEC-2021-236, PYSEC-2021-527, PYSEC-2021-725
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29599
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of the `Split` TFLite operator is vulnerable to a division by zero error(https://github.com/tensorflow/tensorflow/blob/e2752089ef7ce9bcf3db0ec618ebd23ea119d0c7/tensorflow/lite/kernels/split.cc#L63-L65). An attacker can craft a model such that `num_splits` would be 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/b22786e7e9b7bdb6a56936ff29cc7e9968d7bc1d
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-97wf-p777-86jq
- https://nvd.nist.gov/vuln/detail/CVE-2021-29599
