# [M] `CHECK` fail in `BCast` overflow

## Summary
Severity: Medium
Advisory: GHSA-h246-cgh4-7475
CVE: CVE-2022-41890
CWE: CWE-704
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-h246-cgh4-7475
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
If [`BCast::ToShape`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/util/bcast.h) is given input larger than an `int32`, it will crash, despite being supposed to handle up to an `int64`. An example can be seen in [`tf.experimental.numpy.outer`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/util/bcast.h) by passing in large input to the input `b`.
```python
import tensorflow as tf
value = tf.constant(shape=[2, 1024, 1024, 1024], value=False)
tf.experimental.numpy.outer(a=6,b=value)
```

### Patches
We have patched the issue in GitHub commit [8310bf8dd188ff780e7fc53245058215a05bdbe5](https://github.com/tensorflow/tensorflow/commit/8310bf8dd188ff780e7fc53245058215a05bdbe5).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Pattarakrit Rattankul.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h246-cgh4-7475
- https://nvd.nist.gov/vuln/detail/CVE-2022-41890
- https://github.com/tensorflow/tensorflow/commit/8310bf8dd188ff780e7fc53245058215a05bdbe5
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/util/bcast.h
