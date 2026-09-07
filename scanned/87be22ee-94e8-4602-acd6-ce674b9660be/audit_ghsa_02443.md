# [M] Heap OOB in `RaggedGather`

## Summary
Severity: Medium
Advisory: GHSA-9c8h-vvrj-w2p8
CVE: CVE-2021-37641
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9c8h-vvrj-w2p8
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
If the arguments to `tf.raw_ops.RaggedGather` don't determine a valid ragged tensor code can trigger a read from outside of bounds of heap allocated buffers.
                                                                                                                                                                                                                                                                                          
```python
import tensorflow as tf

tf.raw_ops.RaggedGather(
  params_nested_splits = [0,0,0],
  params_dense_values = [1,1],
  indices = [0,0,9,0,0],
  OUTPUT_RAGGED_RANK=0)
```

In debug mode, the same code triggers a `CHECK` failure.

The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/ragged_gather_op.cc#L70) directly reads the first dimension of a tensor shape before checking that said tensor has rank of at least 1 (i.e., it is not a scalar). Furthermore, the implementation does not check that the list given by `params_nested_splits` is not an empty list of tensors.

### Patches
We have patched the issue in GitHub commit [a2b743f6017d7b97af1fe49087ae15f0ac634373](https://github.com/tensorflow/tensorflow/commit/a2b743f6017d7b97af1fe49087ae15f0ac634373).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9c8h-vvrj-w2p8
- https://nvd.nist.gov/vuln/detail/CVE-2021-37641
- https://github.com/tensorflow/tensorflow/commit/a2b743f6017d7b97af1fe49087ae15f0ac634373
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-554.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-752.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-263.yaml
- https://github.com/tensorflow/tensorflow
