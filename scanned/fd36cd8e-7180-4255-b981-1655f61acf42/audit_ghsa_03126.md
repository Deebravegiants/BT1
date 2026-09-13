# [H] Stack overflow due to looping TFLite subgraph

## Summary
Severity: High
Advisory: GHSA-cwv3-863g-39vx
CVE: CVE-2021-29591
CWE: CWE-674, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-cwv3-863g-39vx
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.1.4
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.1.4
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.1.4
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.2

## Details
### Impact
TFlite graphs must not have loops between nodes. However, this condition was not checked and an attacker could craft models that would result in infinite loop during evaluation. In certain cases, the infinite loop would be replaced by stack overflow due to too many recursive calls.

For example, the [`While` implementation](https://github.com/tensorflow/tensorflow/blob/106d8f4fb89335a2c52d7c895b7a7485465ca8d9/tensorflow/lite/kernels/while.cc) could be tricked into a scneario where both the body and the loop subgraphs are the same. Evaluating one of the subgraphs means calling the `Eval` function for the other and this quickly exhaust all stack space.
    
### Patches 
We have patched the issue in GitHub commit [9c1dc920d8ffb4893d6c9d27d1f039607b326743](https://github.com/tensorflow/tensorflow/commit/9c1dc920d8ffb4893d6c9d27d1f039607b326743) (for the `While` operator) and in GitHub commit [c6173f5fe66cdbab74f4f869311fe6aae2ba35f4](https://github.com/tensorflow/tensorflow/commit/c6173f5fe66cdbab74f4f869311fe6aae2ba35f4) (in general).
    
The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution 
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cwv3-863g-39vx
- https://nvd.nist.gov/vuln/detail/CVE-2021-29591
- https://github.com/tensorflow/tensorflow/commit/9c1dc920d8ffb4893d6c9d27d1f039607b326743
- https://github.com/tensorflow/tensorflow/commit/c6173f5fe66cdbab74f4f869311fe6aae2ba35f4
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-519.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-717.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-228.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/106d8f4fb89335a2c52d7c895b7a7485465ca8d9/tensorflow/lite/kernels/while.cc
