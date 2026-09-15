# [M] TensorFlow vulnerable to `CHECK` fail in `AudioSummaryV2`

## Summary
Severity: Medium
Advisory: GHSA-g9h5-vr8m-x2h4
CVE: CVE-2022-35995
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-g9h5-vr8m-x2h4
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
When `AudioSummaryV2` receives an input `sample_rate` with more than one element, it gives a `CHECK` fails that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
arg_0=''
arg_1=tf.random.uniform(shape=(1,1), dtype=tf.float32, maxval=None)
arg_2=tf.random.uniform(shape=(2,1), dtype=tf.float32, maxval=None)
arg_3=3
arg_4=''
tf.raw_ops.AudioSummaryV2(tag=arg_0, tensor=arg_1, sample_rate=arg_2,
                          max_outputs=arg_3, name=arg_4)
```

### Patches
We have patched the issue in GitHub commit [bf6b45244992e2ee543c258e519489659c99fb7f](https://github.com/tensorflow/tensorflow/commit/bf6b45244992e2ee543c258e519489659c99fb7f).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-g9h5-vr8m-x2h4
- https://nvd.nist.gov/vuln/detail/CVE-2022-35995
- https://github.com/tensorflow/tensorflow/commit/bf6b45244992e2ee543c258e519489659c99fb7f
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
