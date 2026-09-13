# [M] Undefined behavior when users supply invalid resource handles

## Summary
Severity: Medium
Advisory: GHSA-5wpj-c6f7-24x8
CVE: CVE-2022-29207
CWE: CWE-20, CWE-475
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5wpj-c6f7-24x8
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
Multiple TensorFlow operations misbehave in eager mode when the resource handle provided to them is invalid:

```python
import tensorflow as tf

tf.raw_ops.QueueIsClosedV2(handle=[])
```

```python
import tensorflow as tf

tf.summary.flush(writer=())
```
  
In graph mode, it would have been impossible to perform these API calls, but migration to TF 2.x eager mode opened up this vulnerability. If the resource handle is empty, then a reference is bound to a null pointer inside TensorFlow codebase (various codepaths). This is undefined behavior.

### Patches
We have patched the issue in GitHub commit [a5b89cd68c02329d793356bda85d079e9e69b4e7](https://github.com/tensorflow/tensorflow/commit/a5b89cd68c02329d793356bda85d079e9e69b4e7) and GitHub commit [dbdd98c37bc25249e8f288bd30d01e118a7b4498](https://github.com/tensorflow/tensorflow/commit/dbdd98c37bc25249e8f288bd30d01e118a7b4498).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Hong Jin from Singapore Management University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5wpj-c6f7-24x8
- https://nvd.nist.gov/vuln/detail/CVE-2022-29207
- https://github.com/tensorflow/tensorflow/commit/a5b89cd68c02329d793356bda85d079e9e69b4e7
- https://github.com/tensorflow/tensorflow/commit/dbdd98c37bc25249e8f288bd30d01e118a7b4498
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
