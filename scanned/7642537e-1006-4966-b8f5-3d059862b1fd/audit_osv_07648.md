# [H] Heap buffer overflow in `MaxPoolGrad`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29579
Aliases: CVE-2021-29579, GHSA-79fv-9865-4qcv, PYSEC-2021-216, PYSEC-2021-507, PYSEC-2021-705
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29579
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.MaxPoolGrad` is vulnerable to a heap buffer overflow. The implementation(https://github.com/tensorflow/tensorflow/blob/ab1e644b48c82cb71493f4362b4dd38f4577a1cf/tensorflow/core/kernels/maxpooling_op.cc#L194-L203) fails to validate that indices used to access elements of input/output arrays are valid. Whereas accesses to `input_backprop_flat` are guarded by `FastBoundsCheck`, the indexing in `out_backprop_flat` can result in OOB access. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/a74768f8e4efbda4def9f16ee7e13cf3922ac5f7
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-79fv-9865-4qcv
- https://nvd.nist.gov/vuln/detail/CVE-2021-29579
