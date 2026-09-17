# [M] Heap out of bounds access in MakeEdge in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-q263-fvxm-m5mw
CVE: CVE-2020-26271
CWE: CWE-125, CWE-908
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2020-12-10
Source: https://github.com/advisories/GHSA-q263-fvxm-m5mw
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <1.15.5
- PyPI: `tensorflow` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.2
- PyPI: `tensorflow-cpu` — affected >=0 <1.15.5
- PyPI: `tensorflow-cpu` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow-cpu` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.2
- PyPI: `tensorflow-gpu` — affected >=0 <1.15.5
- PyPI: `tensorflow-gpu` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow-gpu` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.2

## Details
### Impact
Under certain cases, loading a saved model can result in accessing uninitialized memory while building the computation graph. The [`MakeEdge` function](https://github.com/tensorflow/tensorflow/blob/3616708cb866365301d8e67b43b32b46d94b08a0/tensorflow/core/common_runtime/graph_constructor.cc#L1426-L1438) creates an edge between one output tensor of the `src` node (given by `output_index`) and the input slot of the `dst` node (given by `input_index`). This is only possible if the types of the tensors on both sides coincide, so the function begins by obtaining the corresponding `DataType` values and comparing these for equality:

```cc
  DataType src_out = src->output_type(output_index);
  DataType dst_in = dst->input_type(input_index);
  //...
```

However, there is no check that the indices point to inside of the arrays they index into. Thus, this can result in accessing data out of bounds of the corresponding heap allocated arrays.

In most scenarios, this can manifest as unitialized data access, but if the index points far away from the boundaries of the arrays this can be used to leak addresses from the library.

### Patches
We have patched the issue in GitHub commit [0cc38aaa4064fd9e79101994ce9872c6d91f816b](https://github.com/tensorflow/tensorflow/commit/0cc38aaa4064fd9e79101994ce9872c6d91f816b) and will release TensorFlow 2.4.0 containing the patch. TensorFlow nightly packages after this commit will also have the issue resolved.

Since this issue also impacts TF versions before 2.4, we will patch all releases between 1.15 and 2.3 inclusive.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-q263-fvxm-m5mw
- https://nvd.nist.gov/vuln/detail/CVE-2020-26271
- https://github.com/tensorflow/tensorflow/commit/0cc38aaa4064fd9e79101994ce9872c6d91f816b
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-302.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-337.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-257.yaml
