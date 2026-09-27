# [H] Division by zero in TFLite's implementation of `SpaceToBatchNd`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29597
Aliases: CVE-2021-29597, GHSA-v52p-hfjf-wg88, PYSEC-2021-234, PYSEC-2021-525, PYSEC-2021-723
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29597
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of the `SpaceToBatchNd` TFLite operator is [vulnerable to a division by zero error](https://github.com/tensorflow/tensorflow/blob/412c7d9bb8f8a762c5b266c9e73bfa165f29aac8/tensorflow/lite/kernels/space_to_batch_nd.cc#L82-L83). An attacker can craft a model such that one dimension of the `block` input is 0. Hence, the corresponding value in `block_shape` is 0. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/6d36ba65577006affb272335b7c1abd829010708
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-v52p-hfjf-wg88
- https://nvd.nist.gov/vuln/detail/CVE-2021-29597
