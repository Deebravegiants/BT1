# [H] Heap OOB and CHECK fail in `ResourceGather`

## Summary
Severity: High
Advisory: GHSA-2r8p-fg3c-wcj4
CVE: CVE-2021-37654
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2r8p-fg3c-wcj4
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
An attacker can trigger a crash via a `CHECK`-fail in debug builds of TensorFlow using `tf.raw_ops.ResourceGather` or a read from outside the bounds of heap allocated data in the same API in a release build:

```python
import tensorflow as tf

tensor = tf.constant(value=[[1,2],[3,4],[5,6]],shape=(3,2),dtype=tf.uint32)
v = tf.Variable(tensor)
tf.raw_ops.ResourceGather(
  resource=v.handle,
  indices=[0],
  dtype=tf.uint32,
  batch_dims=10,
  validate_indices=False)
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/f24faa153ad31a4b51578f8181d3aaab77a1ddeb/tensorflow/core/kernels/resource_variable_ops.cc#L660-L668) does not check that the `batch_dims` value that the user supplies is less than the rank of the input tensor.

Since the implementation uses several for loops over the dimensions of `tensor`, this results in reading data from outside the bounds of heap allocated buffer backing the tensor:

```cc
    // batch_dims_ = > params.dims() (10 > 2)
    for (int i = 0; i < batch_dims_; ++i) {
      result_shape.AddDim(params.dim_size(i));
    }
    for (int i = batch_dims_; i < indices.dims(); ++i) {
      result_shape.AddDim(indices.dim_size(i));
    }
    for (int i = batch_dims_ + 1; i < params.dims(); ++i) {
      result_shape.AddDim(params.dim_size(i));
    }
```

In debug mode, `.dim_size(i)` validates that the argument is less than `.dims()` using a `DCHECK`. But the `DCHECK` is a no-op in release builds.

### Patches
We have patched the issue in GitHub commit [bc9c546ce7015c57c2f15c168b3d9201de679a1d](https://github.com/tensorflow/tensorflow/commit/bc9c546ce7015c57c2f15c168b3d9201de679a1d).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-2r8p-fg3c-wcj4
- https://nvd.nist.gov/vuln/detail/CVE-2021-37654
- https://github.com/tensorflow/tensorflow/commit/bc9c546ce7015c57c2f15c168b3d9201de679a1d
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-567.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-765.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-276.yaml
- https://github.com/tensorflow/tensorflow
