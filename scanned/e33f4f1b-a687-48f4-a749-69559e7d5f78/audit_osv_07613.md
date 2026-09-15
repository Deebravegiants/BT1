# [M] CHECK-fail in `CTCGreedyDecoder`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29543
Aliases: CVE-2021-29543, GHSA-fphq-gw9m-ghrv, PYSEC-2021-180, PYSEC-2021-471, PYSEC-2021-669
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29543
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. An attacker can trigger a denial of service via a `CHECK`-fail in `tf.raw_ops.CTCGreedyDecoder`. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/1615440b17b364b875eb06f43d087381f1460a65/tensorflow/core/kernels/ctc_decoder_ops.cc#L37-L50) has a `CHECK_LT` inserted to validate some invariants. When this condition is false, the program aborts, instead of returning a valid error to the user. This abnormal termination can be weaponized in denial of service attacks. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/ea3b43e98c32c97b35d52b4c66f9107452ca8fb2
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-fphq-gw9m-ghrv
- https://nvd.nist.gov/vuln/detail/CVE-2021-29543
