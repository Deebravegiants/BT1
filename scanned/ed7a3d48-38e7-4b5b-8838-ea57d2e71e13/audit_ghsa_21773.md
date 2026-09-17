# [M] Multiple `CHECK`-fails in `function.cc` in TensowFlow

## Summary
Severity: Medium
Advisory: GHSA-43jf-985q-588j
CVE: CVE-2022-23586
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-43jf-985q-588j
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact
A malicious user can cause a denial of service by altering a `SavedModel` such that [assertions in `function.cc`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/framework/function.cc) would be falsified and crash the Python interpreter.
### Patches
We have patched the issue in GitHub commits [dcc21c7bc972b10b6fb95c2fb0f4ab5a59680ec2](https://github.com/tensorflow/tensorflow/commit/dcc21c7bc972b10b6fb95c2fb0f4ab5a59680ec2) and [3d89911481ba6ebe8c88c1c0b595412121e6c645](https://github.com/tensorflow/tensorflow/commit/3d89911481ba6ebe8c88c1c0b595412121e6c645).
  
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-43jf-985q-588j
- https://nvd.nist.gov/vuln/detail/CVE-2022-23586
- https://github.com/tensorflow/tensorflow/commit/3d89911481ba6ebe8c88c1c0b595412121e6c645
- https://github.com/tensorflow/tensorflow/commit/dcc21c7bc972b10b6fb95c2fb0f4ab5a59680ec2
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-95.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-150.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/framework/function.cc
