# [M] Null pointer dereference in `StringNGrams`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29541
Aliases: CVE-2021-29541, GHSA-xqfj-35wv-m3cr, PYSEC-2021-178, PYSEC-2021-469, PYSEC-2021-667
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29541
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a dereference of a null pointer in `tf.raw_ops.StringNGrams`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/1cdd4da14282210cc759e468d9781741ac7d01bf/tensorflow/core/kernels/string_ngrams_op.cc#L67-L74) does not fully validate the `data_splits` argument. This would result in `ngrams_data`(https://github.com/tensorflow/tensorflow/blob/1cdd4da14282210cc759e468d9781741ac7d01bf/tensorflow/core/kernels/string_ngrams_op.cc#L106-L110) to be a null pointer when the output would be computed to have 0 or negative size. Later writes to the output tensor would then cause a null pointer dereference. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/ba424dd8f16f7110eea526a8086f1a155f14f22b
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xqfj-35wv-m3cr
- https://nvd.nist.gov/vuln/detail/CVE-2021-29541
