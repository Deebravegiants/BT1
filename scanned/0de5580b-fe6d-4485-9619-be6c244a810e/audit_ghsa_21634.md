# [H] `CHECK`-failures in Tensorflow

## Summary
Severity: High
Advisory: GHSA-4v5p-v5h9-6xjx
CVE: CVE-2022-23565
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-4v5p-v5h9-6xjx
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
An attacker can trigger denial of service via assertion failure by altering a `SavedModel` on disk such that `AttrDef`s of some operation are duplicated.

### Patches
We have patched the issue in GitHub commit [c2b31ff2d3151acb230edc3f5b1832d2c713a9e0](https://github.com/tensorflow/tensorflow/commit/c2b31ff2d3151acb230edc3f5b1832d2c713a9e0).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4v5p-v5h9-6xjx
- https://nvd.nist.gov/vuln/detail/CVE-2022-23565
- https://github.com/tensorflow/tensorflow/commit/c2b31ff2d3151acb230edc3f5b1832d2c713a9e0
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-74.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-129.yaml
- https://github.com/tensorflow/tensorflow
