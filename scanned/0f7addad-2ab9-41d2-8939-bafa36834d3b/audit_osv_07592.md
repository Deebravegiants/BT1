# [M] Division by 0 in `Conv3DBackprop*`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29522
Aliases: CVE-2021-29522, GHSA-c968-pq7h-7fxv, PYSEC-2021-159, PYSEC-2021-450, PYSEC-2021-648
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29522
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The `tf.raw_ops.Conv3DBackprop*` operations fail to validate that the input tensors are not empty. In turn, this would result in a division by 0. This is because the implementation(https://github.com/tensorflow/tensorflow/blob/a91bb59769f19146d5a0c20060244378e878f140/tensorflow/core/kernels/conv_grad_ops_3d.cc#L430-L450) does not check that the divisor used in computing the shard size is not zero. Thus, if attacker controls the input sizes, they can trigger a denial of service via a division by zero error. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/311403edbc9816df80274bd1ea8b3c0c0f22c3fa
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-c968-pq7h-7fxv
- https://nvd.nist.gov/vuln/detail/CVE-2021-29522
