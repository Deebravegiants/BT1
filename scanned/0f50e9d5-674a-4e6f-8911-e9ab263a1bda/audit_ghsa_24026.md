# [M] Missing validation causes `TensorSummaryV2` to crash

## Summary
Severity: Medium
Advisory: GHSA-2p9q-h29j-3f5v
CVE: CVE-2022-29193
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2p9q-h29j-3f5v
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
The implementation of [`tf.raw_ops.TensorSummaryV2`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/summary_tensor_op.cc#L33-L58) does not fully validate the input arguments. This results in a `CHECK`-failure which can be used to trigger a denial of service attack:

```python
import numpy as np
import tensorflow as tf

tf.raw_ops.TensorSummaryV2(
  tag=np.array('test'),
  tensor=np.array(3),
  serialized_summary_metadata=tf.io.encode_base64(np.empty((0))))
```

The code assumes `axis` is a scalar but there is no validation for this.

```cc
    const Tensor& serialized_summary_metadata_tensor = c->input(2);
    // ...
    ParseFromTString(serialized_summary_metadata_tensor.scalar<tstring>()(),
                     v->mutable_metadata());
``` 

### Patches
We have patched the issue in GitHub commit [290bb05c80c327ed74fae1d089f1001b1e2a4ef7](https://github.com/tensorflow/tensorflow/commit/290bb05c80c327ed74fae1d089f1001b1e2a4ef7).
    
The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.
    
### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
  
### Attribution
This vulnerability has been reported by Neophytos Christou from Secure Systems Lab at Brown University and Hong Jin from Singapore Management University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-2p9q-h29j-3f5v
- https://nvd.nist.gov/vuln/detail/CVE-2022-29193
- https://github.com/tensorflow/tensorflow/commit/290bb05c80c327ed74fae1d089f1001b1e2a4ef7
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/summary_tensor_op.cc#L33-L58
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
