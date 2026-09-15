# [M] TensorFlow vulnerable to `CHECK` fail in `CollectiveGather`

## Summary
Severity: Medium
Advisory: GHSA-fhfc-2q7x-929f
CVE: CVE-2022-35994
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-fhfc-2q7x-929f
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
When `CollectiveGather` receives an scalar input `input`, it gives a `CHECK` fails that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
arg_0=1
arg_1=1
arg_2=1
arg_3=1
arg_4=(3, 3,3)
arg_5='auto'
arg_6=0
arg_7=''
tf.raw_ops.CollectiveGather(input=arg_0, group_size=arg_1, group_key=arg_2,
                            instance_key=arg_3, shape=arg_4,
                            communication_hint=arg_5, timeout_seconds=arg_6, name=arg_7)
```

### Patches
We have patched the issue in GitHub commit [c1f491817dec39a26be3c574e86a88c30f3c4770](https://github.com/tensorflow/tensorflow/commit/c1f491817dec39a26be3c574e86a88c30f3c4770).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-fhfc-2q7x-929f
- https://nvd.nist.gov/vuln/detail/CVE-2022-35994
- https://github.com/tensorflow/tensorflow/commit/c1f491817dec39a26be3c574e86a88c30f3c4770
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
