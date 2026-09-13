# [H] Heap OOB in nested `tf.map_fn` with `RaggedTensor`s

## Summary
Severity: High
Advisory: GHSA-g8wg-cjwc-xhhp
CVE: CVE-2021-37679
CWE: CWE-125, CWE-681
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-g8wg-cjwc-xhhp
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
It is possible to nest a `tf.map_fn` within another `tf.map_fn` call. However, if the input tensor is a `RaggedTensor` and there is no function signature provided, code assumes the output is a fully specified tensor and fills output buffer with uninitialized contents from the heap:

```python
import tensorflow as tf
x = tf.ragged.constant([[1,2,3], [4,5], [6]])
t = tf.map_fn(lambda r: tf.map_fn(lambda y: r, r), x)
z = tf.ragged.constant([[[1,2,3],[1,2,3],[1,2,3]],[[4,5],[4,5]],[[6]]])
```
  
The `t` and `z` outputs should be identical, however this is not the case. The last row of `t` contains data from the heap which can be used to leak other memory information.

The bug lies in the conversion from a `Variant` tensor to a `RaggedTensor`. The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/ragged_tensor_from_variant_op.cc#L177-L190) does not check that all inner shapes match and this results in the additional dimensions in the above example.

The same implementation can result in data loss, if input tensor is tweaked:

```python
import tensorflow as tf
x = tf.ragged.constant([[1,2], [3,4,5], [6]])
t = tf.map_fn(lambda r: tf.map_fn(lambda y: r, r), x) 
```

Here, the output tensor will only have 2 elements for each inner dimension.

### Patches
We have patched the issue in GitHub commit [4e2565483d0ffcadc719bd44893fb7f609bb5f12](https://github.com/tensorflow/tensorflow/commit/4e2565483d0ffcadc719bd44893fb7f609bb5f12).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Haris Sahovic.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-g8wg-cjwc-xhhp
- https://nvd.nist.gov/vuln/detail/CVE-2021-37679
- https://github.com/tensorflow/tensorflow/commit/4e2565483d0ffcadc719bd44893fb7f609bb5f12
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-592.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-790.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-301.yaml
- https://github.com/tensorflow/tensorflow
