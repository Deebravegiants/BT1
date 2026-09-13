# [M] Segfault while copying constant resource tensor

## Summary
Severity: Medium
Advisory: GHSA-786j-5qwq-r36x
CVE: CVE-2021-41204
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-786j-5qwq-r36x
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
During TensorFlow's Grappler optimizer phase, constant folding might attempt to deep copy a resource tensor. This results in a segfault, as these tensors are supposed to not change.

### Patches
We have patched the issue in GitHub commit [7731e8dfbe4a56773be5dc94d631611211156659](https://github.com/tensorflow/tensorflow/commit/7731e8dfbe4a56773be5dc94d631611211156659).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.
    
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-786j-5qwq-r36x
- https://nvd.nist.gov/vuln/detail/CVE-2021-41204
- https://github.com/tensorflow/tensorflow/commit/7731e8dfbe4a56773be5dc94d631611211156659
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-614.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-812.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-397.yaml
- https://github.com/tensorflow/tensorflow
