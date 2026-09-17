# [H] Type confusion during tensor casts lead to dereferencing null pointers

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29513
Aliases: CVE-2021-29513, GHSA-452g-f7fp-9jf7, PYSEC-2021-150, PYSEC-2021-441, PYSEC-2021-639
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29513
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Calling TF operations with tensors of non-numeric types when the operations expect numeric tensors result in null pointer dereferences. The conversion from Python array to C++ array(https://github.com/tensorflow/tensorflow/blob/ff70c47a396ef1e3cb73c90513da4f5cb71bebba/tensorflow/python/lib/core/ndarray_tensor.cc#L113-L169) is vulnerable to a type confusion. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/030af767d357d1b4088c4a25c72cb3906abac489
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-452g-f7fp-9jf7
- https://nvd.nist.gov/vuln/detail/CVE-2021-29513
