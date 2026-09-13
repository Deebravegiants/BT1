# [H] TensorFlow vulnerable to heap out of bounds read in filesystem glob matching

## Summary
Severity: High
Advisory: GHSA-9jjw-hf72-3mxw
CVE: CVE-2020-26269
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-9jjw-hf72-3mxw
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.4.0rc0 <2.4.0
- PyPI: `tensorflow-cpu` — affected >=2.4.0rc0 <2.4.0
- PyPI: `tensorflow-gpu` — affected >=2.4.0rc0 <2.4.0

## Details
### Impact
The general implementation for matching filesystem paths to globbing pattern is vulnerable to an access out of bounds of [the array holding the directories](https://github.com/tensorflow/tensorflow/blob/458c6260265c46ebaf18052d6c61aea4b6b40926/tensorflow/core/platform/file_system_helper.cc#L127):

```cc
if (!fs->Match(child_path, dirs[dir_index])) { ... }
```

Since `dir_index` is [unconditionaly incremented](https://github.com/tensorflow/tensorflow/blob/458c6260265c46ebaf18052d6c61aea4b6b40926/tensorflow/core/platform/file_system_helper.cc#L106) outside of the lambda function where the vulnerable pattern occurs, this results in an access out of bounds issue under certain scenarios. For example, if `/tmp/x` is a directory that only contains a single file `y`, then the following scenario will cause a crash due to the out of bounds read:

```python
>>> tf.io.gfile.glob('/tmp/x/')
Segmentation fault
```

There are multiple invariants and preconditions that are assumed by the parallel implementation of `GetMatchingPaths` but are not verified by the PRs introducing it ([#40861](https://github.com/tensorflow/tensorflow/pull/40861) and [#44310](https://github.com/tensorflow/tensorflow/pull/44310)). Thus, we are completely rewriting the implementation to fully specify and validate these.

### Patches
We have patched the issue in GitHub commit [8b5b9dc96666a3a5d27fad7179ff215e3b74b67c](https://github.com/tensorflow/tensorflow/commit/8b5b9dc96666a3a5d27fad7179ff215e3b74b67c) and will release TensorFlow 2.4.0 containing the patch. TensorFlow nightly packages after this commit will also have the issue resolved.

This issue only impacts master branch and the release candidates for TF version 2.4. The final release of the 2.4 release will be patched.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9jjw-hf72-3mxw
- https://nvd.nist.gov/vuln/detail/CVE-2020-26269
- https://github.com/tensorflow/tensorflow/pull/40861
- https://github.com/tensorflow/tensorflow/pull/44310
- https://github.com/tensorflow/tensorflow/commit/8b5b9dc96666a3a5d27fad7179ff215e3b74b67c
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-300.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-335.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-141.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/458c6260265c46ebaf18052d6c61aea4b6b40926/tensorflow/core/platform/file_system_helper.cc#L106
- https://github.com/tensorflow/tensorflow/blob/458c6260265c46ebaf18052d6c61aea4b6b40926/tensorflow/core/platform/file_system_helper.cc#L127
