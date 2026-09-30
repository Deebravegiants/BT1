# [H] Missing validation during checkpoint loading

## Summary
Severity: High
Advisory: GHSA-7pxj-m4jf-r6h2
CVE: CVE-2021-41203
CWE: CWE-190, CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-7pxj-m4jf-r6h2
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
An attacker can trigger undefined behavior, integer overflows, segfaults and `CHECK`-fail crashes if they can change saved checkpoints from outside of TensorFlow.

This is because the checkpoints loading infrastructure is missing validation for invalid file formats.

### Patches
We have patched the issue in GitHub commits [b619c6f865715ca3b15ef1842b5b95edbaa710ad](https://github.com/tensorflow/tensorflow/commit/b619c6f865715ca3b15ef1842b5b95edbaa710ad), [e8dc63704c88007ee4713076605c90188d66f3d2](https://github.com/tensorflow/tensorflow/commit/e8dc63704c88007ee4713076605c90188d66f3d2), [368af875869a204b4ac552b9ddda59f6a46a56ec](https://github.com/tensorflow/tensorflow/commit/368af875869a204b4ac552b9ddda59f6a46a56ec), and [abcced051cb1bd8fb05046ac3b6023a7ebcc4578](https://github.com/tensorflow/tensorflow/commit/abcced051cb1bd8fb05046ac3b6023a7ebcc4578).

These fixes will be included in TensorFlow 2.7.0. We will also cherrypick these commits on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7pxj-m4jf-r6h2
- https://nvd.nist.gov/vuln/detail/CVE-2021-41203
- https://github.com/tensorflow/tensorflow/commit/368af875869a204b4ac552b9ddda59f6a46a56ec
- https://github.com/tensorflow/tensorflow/commit/abcced051cb1bd8fb05046ac3b6023a7ebcc4578
- https://github.com/tensorflow/tensorflow/commit/b619c6f865715ca3b15ef1842b5b95edbaa710ad
- https://github.com/tensorflow/tensorflow/commit/e8dc63704c88007ee4713076605c90188d66f3d2
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-613.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-811.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-396.yaml
- https://github.com/tensorflow/tensorflow
