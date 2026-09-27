# [M] Crash in `tf.strings.substr` due to `CHECK`-fail

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29617
Aliases: CVE-2021-29617, GHSA-mmq6-q8r3-48fm, PYSEC-2021-254, PYSEC-2021-545, PYSEC-2021-743
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29617
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a denial of service via `CHECK`-fail in `tf.strings.substr` with invalid arguments. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/issues/46900
- https://github.com/tensorflow/issues/46974
- https://github.com/tensorflow/tensorflow/commit/890f7164b70354c57d40eda52dcdd7658677c09f
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mmq6-q8r3-48fm
- https://nvd.nist.gov/vuln/detail/CVE-2021-29617
