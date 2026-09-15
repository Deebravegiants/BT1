# [M] Null pointer dereference via invalid Ragged Tensors

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29516
Aliases: CVE-2021-29516, GHSA-84mw-34w6-2q43, PYSEC-2021-153, PYSEC-2021-444, PYSEC-2021-642
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29516
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Calling `tf.raw_ops.RaggedTensorToVariant` with arguments specifying an invalid ragged tensor results in a null pointer dereference. The implementation of `RaggedTensorToVariant` operations(https://github.com/tensorflow/tensorflow/blob/904b3926ed1c6c70380d5313d282d248a776baa1/tensorflow/core/kernels/ragged_tensor_to_variant_op.cc#L39-L40) does not validate that the ragged tensor argument is non-empty. Since `batched_ragged` contains no elements, `batched_ragged.splits` is a null vector, thus `batched_ragged.splits(0)` will result in dereferencing `nullptr`. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/b055b9c474cd376259dde8779908f9eeaf097d93
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-84mw-34w6-2q43
- https://nvd.nist.gov/vuln/detail/CVE-2021-29516
