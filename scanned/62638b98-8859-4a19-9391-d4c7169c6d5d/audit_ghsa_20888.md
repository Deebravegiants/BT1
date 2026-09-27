# [M] TensorFlow vulnerable to `CHECK` failure in `SobolSample` via missing validation

## Summary
Severity: Medium
Advisory: GHSA-97p7-w86h-vcf9
CVE: CVE-2022-35935
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-97p7-w86h-vcf9
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
The implementation of SobolSampleOp is vulnerable to a denial of service via CHECK-failure (assertion failure) caused by assuming `input(0)`, `input(1)`, and `input(2)` to be scalar.
```python
import tensorflow as tf
tf.raw_ops.SobolSample(dim=tf.constant([1,0]), num_results=tf.constant([1]), skip=tf.constant([1]))
```

### Patches
We have patched the issue in GitHub commit [c65c67f88ad770662e8f191269a907bf2b94b1bf](https://github.com/tensorflow/tensorflow/commit/c65c67f88ad770662e8f191269a907bf2b94b1bf).


The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by:
- Kang Hong Jin from Singapore Management University
- Neophytos Christou, Secure Systems Labs, Brown University
- 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-97p7-w86h-vcf9
- https://nvd.nist.gov/vuln/detail/CVE-2022-35935
- https://github.com/tensorflow/tensorflow/commit/c65c67f88ad770662e8f191269a907bf2b94b1bf
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
