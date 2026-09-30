# [H] Division by zero in TFLite's implementation of `SVDF`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29598
Aliases: CVE-2021-29598, GHSA-pmpr-55fj-r229, PYSEC-2021-235, PYSEC-2021-526, PYSEC-2021-724
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29598
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of the `SVDF` TFLite operator is vulnerable to a division by zero error(https://github.com/tensorflow/tensorflow/blob/7f283ff806b2031f407db64c4d3edcda8fb9f9f5/tensorflow/lite/kernels/svdf.cc#L99-L102). An attacker can craft a model such that `params->rank` would be 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/6841e522a3e7d48706a02e8819836e809f738682
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-pmpr-55fj-r229
- https://nvd.nist.gov/vuln/detail/CVE-2021-29598
