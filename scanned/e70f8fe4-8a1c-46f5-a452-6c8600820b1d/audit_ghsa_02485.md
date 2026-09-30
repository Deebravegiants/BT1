# [H] Null pointer dereference in `SparseTensorSliceDataset`

## Summary
Severity: High
Advisory: GHSA-c5x2-p679-95wc
CVE: CVE-2021-37647
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-c5x2-p679-95wc
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
When a user does not supply arguments that determine a valid sparse tensor, `tf.raw_ops.SparseTensorSliceDataset` implementation can be made to dereference a null pointer:

```python
import tensorflow as tf

tf.raw_ops.SparseTensorSliceDataset(
  indices=[[],[],[]],
  values=[1,2,3],
  dense_shape=[3,3])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/data/sparse_tensor_slice_dataset_op.cc#L240-L251) has some argument validation but fails to consider the case when either `indices` or `values` are provided for an empty sparse tensor when the other is not.

If `indices` is empty (as in the example above), then [code that performs validation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/data/sparse_tensor_slice_dataset_op.cc#L260-L261) (i.e., checking that the indices are monotonically increasing) results in a null pointer dereference: 

```cc
    for (int64_t i = 0; i < indices->dim_size(0); ++i) {
      int64_t next_batch_index = indices->matrix<int64>()(i, 0);
      ...
    }
```

If `indices` as provided by the user is empty, then `indices` in the C++ code above is backed by an empty `std::vector`, hence calling `indices->dim_size(0)` results in null pointer dereferencing (same as calling `std::vector::at()` on an empty vector).

### Patches
We have patched the issue in GitHub commit [02cc160e29d20631de3859c6653184e3f876b9d7](https://github.com/tensorflow/tensorflow/commit/02cc160e29d20631de3859c6653184e3f876b9d7).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-c5x2-p679-95wc
- https://nvd.nist.gov/vuln/detail/CVE-2021-37647
- https://github.com/tensorflow/tensorflow/commit/02cc160e29d20631de3859c6653184e3f876b9d7
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-560.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-758.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-269.yaml
- https://github.com/tensorflow/tensorflow
