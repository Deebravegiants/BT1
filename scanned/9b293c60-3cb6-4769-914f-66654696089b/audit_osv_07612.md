# [M] Heap buffer overflow in `StringNGrams`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29542
Aliases: CVE-2021-29542, GHSA-4hrh-9vmp-2jgg, PYSEC-2021-179, PYSEC-2021-470, PYSEC-2021-668
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29542
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can cause a heap buffer overflow by passing crafted inputs to `tf.raw_ops.StringNGrams`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/1cdd4da14282210cc759e468d9781741ac7d01bf/tensorflow/core/kernels/string_ngrams_op.cc#L171-L185) fails to consider corner cases where input would be split in such a way that the generated tokens should only contain padding elements. If input is such that `num_tokens` is 0, then, for `data_start_index=0` (when left padding is present), the marked line would result in reading `data[-1]`. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/ba424dd8f16f7110eea526a8086f1a155f14f22b
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4hrh-9vmp-2jgg
- https://nvd.nist.gov/vuln/detail/CVE-2021-29542
