# [H] Reachable Assertion in Tensorflow

## Summary
Severity: High
Advisory: GHSA-j3mj-fhpq-qqjj
CVE: CVE-2022-23571
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-j3mj-fhpq-qqjj
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
When decoding a tensor from protobuf, a TensorFlow process can encounter cases where a `CHECK` assertion is invalidated based on user controlled arguments, if the tensors have an invalid `dtype` and 0 elements or an invalid shape. This allows attackers to cause denial of services in TensorFlow processes.

### Patches
We have patched the issue in GitHub commit [5b491cd5e41ad63735161cec9c2a568172c8b6a3](https://github.com/tensorflow/tensorflow/commit/5b491cd5e41ad63735161cec9c2a568172c8b6a3).
  
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range. 
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-j3mj-fhpq-qqjj
- https://nvd.nist.gov/vuln/detail/CVE-2022-23571
- https://github.com/tensorflow/tensorflow/commit/5b491cd5e41ad63735161cec9c2a568172c8b6a3
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-80.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-135.yaml
- https://github.com/tensorflow/tensorflow
