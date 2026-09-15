# [H] Insecure temporary file in Tensorflow

## Summary
Severity: High
Advisory: GHSA-wc4g-r73w-x8mm
CVE: CVE-2022-23563
CWE: CWE-367, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-wc4g-r73w-x8mm
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
In multiple places, TensorFlow uses `tempfile.mktemp` to create temporary files. While this is acceptable in testing, in utilities and libraries it is dangerous as a different process can create the file between the check for the filename in `mktemp` and the actual creation of the file by a subsequent operation (a TOC/TOU type of weakness).

In several instances, TensorFlow was supposed to actually create a temporary directory instead of a file. This logic bug is hidden away by the `mktemp` function usage.

### Patches
We have patched the issue in several commits, replacing `mktemp` with the safer `mkstemp`/`mkdtemp` functions, according to the usage pattern.
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported on huntr.dev for one scenario and discovered via variant analysis on other instances.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wc4g-r73w-x8mm
- https://nvd.nist.gov/vuln/detail/CVE-2022-23563
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-72.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-127.yaml
- https://github.com/tensorflow/tensorflow
