# [H] Undefined behavior in `MaxPool3DGradGrad`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29574
Aliases: CVE-2021-29574, GHSA-828x-qc2p-wprq, PYSEC-2021-211, PYSEC-2021-502, PYSEC-2021-700
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29574
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of `tf.raw_ops.MaxPool3DGradGrad` exhibits undefined behavior by dereferencing null pointers backing attacker-supplied empty tensors. The implementation(https://github.com/tensorflow/tensorflow/blob/72fe792967e7fd25234342068806707bbc116618/tensorflow/core/kernels/pooling_ops_3d.cc#L679-L703) fails to validate that the 3 tensor inputs are not empty. If any of them is empty, then accessing the elements in the tensor results in dereferencing a null pointer. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/a3d9f9be9ac2296615644061b40cefcee341dcc4
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-828x-qc2p-wprq
- https://nvd.nist.gov/vuln/detail/CVE-2021-29574
