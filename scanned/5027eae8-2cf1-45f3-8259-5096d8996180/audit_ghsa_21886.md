# [M] `CHECK`-failures in binary ops in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-gjqc-q9g6-q2j3
CVE: CVE-2022-23583
CWE: CWE-617, CWE-843
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-gjqc-q9g6-q2j3
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact
A malicious user can cause a denial of service by altering a `SavedModel` such that [any binary op](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/kernels/cwise_ops_common.h#L88-L137) would trigger `CHECK` failures. This occurs when the protobuf part corresponding to the tensor arguments is modified such that the `dtype` no longer matches the `dtype` expected by the op. In that case, calling the templated binary operator for the binary op would receive corrupted data, due to the type confusion involved:

```cc
functor::BinaryFunctor<Device, Functor, 1>()(
    eigen_device, out->template flat<Tout>(),
    input_0.template flat<Tin>(), input_1.template flat<Tin>(),
    error_ptr);
```
If `Tin` and `Tout` don't match the type of data in `out` and `input_*` tensors then `flat<*>` would interpret it wrongly. In most cases, this would be a silent failure, but we have noticed scenarios where this results in a `CHECK` crash, hence a denial of service.

### Patches
We have patched the issue in GitHub commit [a7c02f1a9bbc35473969618a09ee5f9f5d3e52d9](https://github.com/tensorflow/tensorflow/commit/a7c02f1a9bbc35473969618a09ee5f9f5d3e52d9).
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gjqc-q9g6-q2j3
- https://nvd.nist.gov/vuln/detail/CVE-2022-23583
- https://github.com/tensorflow/tensorflow/commit/a7c02f1a9bbc35473969618a09ee5f9f5d3e52d9
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-92.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-147.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/kernels/cwise_ops_common.h#L88-L137
