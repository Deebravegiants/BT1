# [H] Memory corruption in Tensorflow

## Summary
Severity: High
Advisory: GHSA-rjjg-hgv6-h69v
CVE: CVE-2020-15193
CWE: CWE-908
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-rjjg-hgv6-h69v
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The implementation of `dlpack.to_dlpack` can be made to use uninitialized memory resulting in further memory corruption. This is because the pybind11 glue code assumes that the argument is a tensor:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/python/tfe_wrapper.cc#L1361

However, there is nothing stopping users from passing in a Python object instead of a tensor.
```python
In [2]: tf.experimental.dlpack.to_dlpack([2])                                                                                                                                            
==1720623==WARNING: MemorySanitizer: use-of-uninitialized-value                                                                                                                            
    #0 0x55b0ba5c410a in tensorflow::(anonymous namespace)::GetTensorFromHandle(TFE_TensorHandle*, TF_Status*) third_party/tensorflow/c/eager/dlpack.cc:46:7
    #1 0x55b0ba5c38f4 in tensorflow::TFE_HandleToDLPack(TFE_TensorHandle*, TF_Status*) third_party/tensorflow/c/eager/dlpack.cc:252:26
... 
```

The uninitialized memory address is due to a `reinterpret_cast`
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/python/eager/pywrap_tensor.cc#L848-L850

Since the `PyObject` is a Python object, not a TensorFlow Tensor, the cast to `EagerTensor` fails. 

### Patches
We have patched the issue in 22e07fb204386768e5bcbea563641ea11f96ceb8 and will release a patch release for all affected versions.

We recommend users to upgrade to TensorFlow 2.2.1 or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rjjg-hgv6-h69v
- https://nvd.nist.gov/vuln/detail/CVE-2020-15193
- https://github.com/tensorflow/tensorflow/commit/22e07fb204386768e5bcbea563641ea11f96ceb8
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-273.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-308.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-116.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
