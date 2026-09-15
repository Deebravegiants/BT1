# [M] Division by zero in TFLite's implementation of hashtable lookup

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29604
Aliases: CVE-2021-29604, GHSA-8rm6-75mf-7r7r, PYSEC-2021-241, PYSEC-2021-532, PYSEC-2021-730
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29604
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The TFLite implementation of hashtable lookup is vulnerable to a division by zero error(https://github.com/tensorflow/tensorflow/blob/1a8e885b864c818198a5b2c0cbbeca5a1e833bc8/tensorflow/lite/kernels/hashtable_lookup.cc#L114-L115) An attacker can craft a model such that `values`'s first dimension would be 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/5117e0851348065ed59c991562c0ec80d9193db2
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8rm6-75mf-7r7r
- https://nvd.nist.gov/vuln/detail/CVE-2021-29604
