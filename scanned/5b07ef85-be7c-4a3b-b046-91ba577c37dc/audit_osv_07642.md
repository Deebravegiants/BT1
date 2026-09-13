# [M] Reference binding to nullptr in `SdcaOptimizer`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29572
Aliases: CVE-2021-29572, GHSA-5gqf-456p-4836, PYSEC-2021-209, PYSEC-2021-500, PYSEC-2021-698
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29572
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.SdcaOptimizer` triggers undefined behavior due to dereferencing a null pointer. The implementation(https://github.com/tensorflow/tensorflow/blob/60a45c8b6192a4699f2e2709a2645a751d435cc3/tensorflow/core/kernels/sdca_internal.cc) does not validate that the user supplied arguments satisfy all constraints expected by the op(https://www.tensorflow.org/api_docs/python/tf/raw_ops/SdcaOptimizer). The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/f7cc8755ac6683131fdfa7a8a121f9d7a9dec6fb
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5gqf-456p-4836
- https://nvd.nist.gov/vuln/detail/CVE-2021-29572
