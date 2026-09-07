# [M] Missing validation causes denial of service via `Conv3DBackpropFilterV2`

## Summary
Severity: Medium
Advisory: GHSA-hx9q-2mx4-m4pg
CVE: CVE-2022-29204
CWE: CWE-191, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hx9q-2mx4-m4pg
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
The implementation of [`tf.raw_ops.UnsortedSegmentJoin`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/unsorted_segment_join_op.cc#L83-L148) does not fully validate the input arguments. This results in a `CHECK`-failure which can be used to trigger a denial of service attack:

```python
import tensorflow as tf

tf.strings.unsorted_segment_join(
  inputs=['123'],
  segment_ids=[0],
  num_segments=-1)
```

The code assumes `num_segments` is a positive scalar but there is no validation:

```cc
const Tensor& num_segments_tensor = context->input(2);
auto num_segments = num_segments_tensor.scalar<NUM_SEGMENTS_TYPE>()();
// ...
Tensor* output_tensor = nullptr;
TensorShape output_shape =
    GetOutputShape(input_shape, segment_id_shape, num_segments);
```

Since this value is used to allocate the output tensor, a negative value would result in a `CHECK`-failure (assertion failure), as per [TFSA-2021-198](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-198.md).

### Patches 
We have patched the issue in GitHub commit [84563f265f28b3c36a15335c8b005d405260e943](https://github.com/tensorflow/tensorflow/commit/84563f265f28b3c36a15335c8b005d405260e943) and GitHub commit [20cb18724b0bf6c09071a3f53434c4eec53cc147](https://github.com/tensorflow/tensorflow/commit/20cb18724b0bf6c09071a3f53434c4eec53cc147).
  
The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.
      
### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
                       
### Attribution 
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/55305).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hx9q-2mx4-m4pg
- https://nvd.nist.gov/vuln/detail/CVE-2022-29204
- https://github.com/tensorflow/tensorflow/commit/20cb18724b0bf6c09071a3f53434c4eec53cc147
- https://github.com/tensorflow/tensorflow/commit/84563f265f28b3c36a15335c8b005d405260e943
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/unsorted_segment_join_op.cc#L83-L14
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-198.md
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
