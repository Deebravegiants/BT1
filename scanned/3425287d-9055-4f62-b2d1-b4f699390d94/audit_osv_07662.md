# [H] Division by zero in TFLite's implementation of `EmbeddingLookup`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29596
Aliases: CVE-2021-29596, GHSA-4vrf-ff7v-hpgr, PYSEC-2021-233, PYSEC-2021-524, PYSEC-2021-722
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29596
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of the `EmbeddingLookup` TFLite operator is vulnerable to a division by zero error(https://github.com/tensorflow/tensorflow/blob/e4b29809543b250bc9b19678ec4776299dd569ba/tensorflow/lite/kernels/embedding_lookup.cc#L73-L74). An attacker can craft a model such that the first dimension of the `value` input is 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/f61c57bd425878be108ec787f4d96390579fb83e
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4vrf-ff7v-hpgr
- https://nvd.nist.gov/vuln/detail/CVE-2021-29596
