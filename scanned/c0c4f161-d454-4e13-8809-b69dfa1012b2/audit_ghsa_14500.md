# [H] TensorFlow has Null Pointer Error in SparseSparseMaximum

## Summary
Severity: High
Advisory: GHSA-558h-mq8x-7q9g
CVE: CVE-2023-25665
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-558h-mq8x-7q9g
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
When `SparseSparseMaximum` is given invalid sparse tensors as inputs, it can give an NPE. 

```python
import tensorflow as tf
tf.raw_ops.SparseSparseMaximum(
 a_indices=[[1]],
 a_values =[ 0.1 ],
 a_shape = [2],
 b_indices=[[]],
 b_values =[2 ],
 b_shape = [2],
)
```

### Patches
We have patched the issue in GitHub commit [5e0ecfb42f5f65629fd7a4edd6c4afe7ff0feb04](https://github.com/tensorflow/tensorflow/commit/5e0ecfb42f5f65629fd7a4edd6c4afe7ff0feb04).

The fix will be included in TensorFlow 2.12. We will also cherrypick this commit on TensorFlow 2.11.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Yu Tian of Qihoo 360 AIVul Team

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-558h-mq8x-7q9g
- https://nvd.nist.gov/vuln/detail/CVE-2023-25665
- https://github.com/tensorflow/tensorflow/commit/5e0ecfb42f5f65629fd7a4edd6c4afe7ff0feb04
- https://github.com/tensorflow/tensorflow
