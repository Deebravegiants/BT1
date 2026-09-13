# [H] Incomplete validation in MKL requantization

## Summary
Severity: High
Advisory: GHSA-v82p-hv3v-p6qp
CVE: CVE-2021-37665
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-v82p-hv3v-p6qp
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
Due to incomplete validation in MKL implementation of requantization, an  attacker can trigger undefined behavior via binding a reference to a null pointer or can access data outside the bounds of heap allocated arrays:

```python
import tensorflow as tf

tf.raw_ops.RequantizationRangePerChannel(
  input=[],
  input_min=[0,0,0,0,0],
  input_max=[1,1,1,1,1],
  clip_value_max=1)
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/mkl/mkl_requantization_range_per_channel_op.cc) does not validate the dimensions of the `input` tensor.

A similar issue occurs in `MklRequantizePerChannelOp`:

```python
import tensorflow as tf 
from tensorflow.python.ops import gen_math_ops

gen_math_ops.requantize_per_channel(
  input=[],
  input_min=[-100,-100,-100,-100,-100],
  input_max=[-100,-100,-100],
  requested_output_min=[-100,-100,-100,-100,-100],
  requested_output_max=[],
  out_type=tf.int)
``` 

The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/mkl/mkl_requantize_per_channel_op.cc) does not perform full validation for all the input arguments.

### Patches
We have patched the issue in GitHub commit [9e62869465573cb2d9b5053f1fa02a81fce21d69](https://github.com/tensorflow/tensorflow/commit/9e62869465573cb2d9b5053f1fa02a81fce21d69) and in the Github commit [203214568f5bc237603dbab6e1fd389f1572f5c9](https://github.com/tensorflow/tensorflow/commit/203214568f5bc237603dbab6e1fd389f1572f5c9).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-v82p-hv3v-p6qp
- https://nvd.nist.gov/vuln/detail/CVE-2021-37665
- https://github.com/tensorflow/tensorflow/commit/203214568f5bc237603dbab6e1fd389f1572f5c9
- https://github.com/tensorflow/tensorflow/commit/9e62869465573cb2d9b5053f1fa02a81fce21d69
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-578.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-776.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-287.yaml
- https://github.com/tensorflow/tensorflow
