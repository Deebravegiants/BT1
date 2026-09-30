# [M] Heap OOB in `UpperBound` and `LowerBound`

## Summary
Severity: Medium
Advisory: GHSA-9697-98pf-4rw7
CVE: CVE-2021-37670
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9697-98pf-4rw7
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
An attacker can read from outside of bounds of heap allocated data by sending specially crafted illegal arguments to `tf.raw_ops.UpperBound`:

```python
import tensorflow as tf
  
tf.raw_ops.UpperBound(
  sorted_input=[1,2,3],
  values=tf.constant(value=[[0,0,0],[1,1,1],[2,2,2]],dtype=tf.int64),
  out_type=tf.int64)
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/searchsorted_op.cc#L85-L104) does not validate the rank of `sorted_input` argument:

```cc
  void Compute(OpKernelContext* ctx) override {
    const Tensor& sorted_inputs_t = ctx->input(0);
    // ...
    OP_REQUIRES(ctx, sorted_inputs_t.dim_size(0) == values_t.dim_size(0),
                Status(error::INVALID_ARGUMENT,
                       "Leading dim_size of both tensors must match."));
    // ...
    if (output_t->dtype() == DT_INT32) {
      OP_REQUIRES(ctx,
                  FastBoundsCheck(sorted_inputs_t.dim_size(1), ...));
      // ...
    }
```

As we access the first two dimensions of `sorted_inputs_t` tensor, it must have rank at least 2.

A similar issue occurs in `tf.raw_ops.LowerBound`.

### Patches
We have patched the issue in GitHub commit [42459e4273c2e47a3232cc16c4f4fff3b3a35c38](https://github.com/tensorflow/tensorflow/commit/42459e4273c2e47a3232cc16c4f4fff3b3a35c38).
  
The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9697-98pf-4rw7
- https://nvd.nist.gov/vuln/detail/CVE-2021-37670
- https://github.com/tensorflow/tensorflow/commit/42459e4273c2e47a3232cc16c4f4fff3b3a35c38
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-583.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-781.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-292.yaml
- https://github.com/tensorflow/tensorflow
