# [M] Use of unitialized value in TFLite

## Summary
Severity: Medium
Advisory: GHSA-4c4g-crqm-xrxw
CVE: CVE-2021-37682
CWE: CWE-908
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4c4g-crqm-xrxw
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
All TFLite operations that use quantization can be made to use unitialized values. [For example](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/lite/kernels/depthwise_conv.cc#L198-L200):

```cc
    const auto* affine_quantization =
        reinterpret_cast<TfLiteAffineQuantization*>(
            filter->quantization.params);
```

The issue stems from the fact that `quantization.params` is only valid if `quantization.type` is different that `kTfLiteNoQuantization`. However, these checks are missing in large parts of the code.

### Patches
We have patched the issue in GitHub commits [537bc7c723439b9194a358f64d871dd326c18887](https://github.com/tensorflow/tensorflow/commit/537bc7c723439b9194a358f64d871dd326c18887),
[4a91f2069f7145aab6ba2d8cfe41be8a110c18a5](https://github.com/tensorflow/tensorflow/commit/4a91f2069f7145aab6ba2d8cfe41be8a110c18a5) and [8933b8a21280696ab119b63263babdb54c298538](https://github.com/tensorflow/tensorflow/commit/8933b8a21280696ab119b63263babdb54c298538).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution 
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4c4g-crqm-xrxw
- https://nvd.nist.gov/vuln/detail/CVE-2021-37682
- https://github.com/tensorflow/tensorflow/commit/4a91f2069f7145aab6ba2d8cfe41be8a110c18a5
- https://github.com/tensorflow/tensorflow/commit/537bc7c723439b9194a358f64d871dd326c18887
- https://github.com/tensorflow/tensorflow/commit/8933b8a21280696ab119b63263babdb54c298538
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-595.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-793.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-304.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/lite/kernels/depthwise_conv.cc#L198-L200
