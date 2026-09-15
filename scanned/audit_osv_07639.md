# [H] Heap out of bounds read in `RequantizationRange`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29569
Aliases: CVE-2021-29569, GHSA-3h8m-483j-7xxm, PYSEC-2021-206, PYSEC-2021-497, PYSEC-2021-695
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29569
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.MaxPoolGradWithArgmax` can cause reads outside of bounds of heap allocated data if attacker supplies specially crafted inputs. The implementation(https://github.com/tensorflow/tensorflow/blob/ac328eaa3870491ababc147822cd04e91a790643/tensorflow/core/kernels/requantization_range_op.cc#L49-L50) assumes that the `input_min` and `input_max` tensors have at least one element, as it accesses the first element in two arrays. If the tensors are empty, `.flat<T>()` is an empty object, backed by an empty array. Hence, accesing even the 0th element is a read outside the bounds. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/ef0c008ee84bad91ec6725ddc42091e19a30cf0e
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-3h8m-483j-7xxm
- https://nvd.nist.gov/vuln/detail/CVE-2021-29569
