# [M] Division by zero in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-v3f7-j968-4h5f
CVE: CVE-2022-21725
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-v3f7-j968-4h5f
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
The [estimator for the cost of some convolution operations](https://github.com/tensorflow/tensorflow/blob/ffa202a17ab7a4a10182b746d230ea66f021fe16/tensorflow/core/grappler/costs/op_level_cost_estimator.cc#L189-L198) can be made to execute a division by 0:

```python
import tensorflow as tf

@tf.function
def test():
  y=tf.raw_ops.AvgPoolGrad(
    orig_input_shape=[1,1,1,1],
    grad=[[[[1.0],[1.0],[1.0]]],[[[2.0],[2.0],[2.0]]],[[[3.0],[3.0],[3.0]]]],
    ksize=[1,1,1,1],
    strides=[1,1,1,0],
    padding='VALID',
    data_format='NCHW')
  return y

test()
```

The function fails to check that the stride argument is stricly positive:

```cc
int64_t GetOutputSize(const int64_t input, const int64_t filter,
                      const int64_t stride, const Padding& padding) {
  // Logic for calculating output shape is from GetWindowedOutputSizeVerbose() 
  // function in third_party/tensorflow/core/framework/common_shape_fns.cc.
  if (padding == Padding::VALID) {
    return (input - filter + stride) / stride;
  } else {  // SAME.
    return (input + stride - 1) / stride;
  }
} 
```

Hence, the fix is to add a check for the stride argument to ensure it is valid.

### Patches
We have patched the issue in GitHub commit [3218043d6d3a019756607643cf65574fbfef5d7a](https://github.com/tensorflow/tensorflow/commit/3218043d6d3a019756607643cf65574fbfef5d7a).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yu Tian of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-v3f7-j968-4h5f
- https://nvd.nist.gov/vuln/detail/CVE-2022-21725
- https://github.com/tensorflow/tensorflow/commit/3218043d6d3a019756607643cf65574fbfef5d7a
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-49.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-104.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/ffa202a17ab7a4a10182b746d230ea66f021fe16/tensorflow/core/grappler/costs/op_level_cost_estimator.cc#L189-L198
