# [H] Heap OOB write in TFLite

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29603
Aliases: CVE-2021-29603, GHSA-crch-j389-5f84, PYSEC-2021-240, PYSEC-2021-531, PYSEC-2021-729
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29603
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. A specially crafted TFLite model could trigger an OOB write on heap in the TFLite implementation of `ArgMin`/`ArgMax`(https://github.com/tensorflow/tensorflow/blob/102b211d892f3abc14f845a72047809b39cc65ab/tensorflow/lite/kernels/arg_min_max.cc#L52-L59). If `axis_value` is not a value between 0 and `NumDimensions(input)`, then the condition in the `if` is never true, so code writes past the last valid element of `output_dims->data`. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/c59c37e7b2d563967da813fa50fe20b21f4da683
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-crch-j389-5f84
- https://nvd.nist.gov/vuln/detail/CVE-2021-29603
