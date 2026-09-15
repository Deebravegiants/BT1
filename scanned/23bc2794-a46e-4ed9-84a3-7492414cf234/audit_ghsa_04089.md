# [C] Integer Overflow or Wraparound in Google TensorFlow

## Summary
Severity: Critical
Advisory: GHSA-mw6v-crh8-8533
CVE: CVE-2018-7575
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-30
Source: https://github.com/advisories/GHSA-mw6v-crh8-8533
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=1.0.0 <1.7.1
- PyPI: `tensorflow-gpu` — affected >=1.0.0 <1.7.1

## Details
### Issue Description
Google TensorFlow 1.7.x and earlier is affected by a Buffer Overflow vulnerability. The type of exploitation is context-dependent. The block size in meta file might contain a large int64 value which causes an integer overflow upon addition. Subsequent code using n as index may cause an out-of-bounds read.

### Impact
A maliciously crafted meta checkpoint could be used to cause the TensorFlow process to perform an out of bounds read on in process memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7575
- https://github.com/tensorflow/tensorflow/commit/d107fee1e4a9a4462f01564798d345802acc2aef
- https://github.com/advisories/GHSA-mw6v-crh8-8533
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2019-223.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2019-230.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2019-205.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2018-004.md
