# [M] Use after free and segfault in shape inference functions

## Summary
Severity: Medium
Advisory: GHSA-3hxh-8cp2-g4hg
CVE: CVE-2021-37690
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3hxh-8cp2-g4hg
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
When running shape functions, some functions (such as `MutableHashTableShape`) produce extra output information in the form of a `ShapeAndType` struct. The shapes embedded in this struct are owned by an inference context that is cleaned up almost immediately; if the upstream code attempts to access this shape information, it can trigger a segfault.

`ShapeRefiner` is mitigating this for normal output shapes by cloning them (and thus putting the newly created shape under ownership of an inference context that will not die), but we were not doing the same for shapes and types. This commit fixes that by doing similar logic on output shapes and types.

### Patches
We have patched the issue in GitHub commit [ee119d4a498979525046fba1c3dd3f13a039fbb1](https://github.com/tensorflow/tensorflow/commit/ee119d4a498979525046fba1c3dd3f13a039fbb1).                                                                                                          

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-3hxh-8cp2-g4hg
- https://nvd.nist.gov/vuln/detail/CVE-2021-37690
- https://github.com/tensorflow/tensorflow/commit/ee119d4a498979525046fba1c3dd3f13a039fbb1
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-603.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-801.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-312.yaml
- https://github.com/tensorflow/tensorflow
