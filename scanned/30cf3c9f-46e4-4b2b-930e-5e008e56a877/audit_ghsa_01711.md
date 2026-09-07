# [H] Out-of-bounds read in TensorFlow possibly causing disclosure of the contents of process memory.

## Summary
Severity: High
Advisory: GHSA-h98h-8mxr-m8gx
CVE: CVE-2018-21233
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-h98h-8mxr-m8gx
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <1.7.0
- PyPI: `tensorflow-gpu` — affected >=0 <1.7.0

## Details
TensorFlow before 1.7.0 has an integer overflow that causes an out-of-bounds read, possibly causing disclosure of the contents of process memory. This occurs in the DecodeBmp feature of the BMP decoder in `core/kernels/decode_bmp_op.cc`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21233
- https://github.com/tensorflow/tensorflow/commit/49f73c55d56edffebde4bca4a407ad69c1cae433
- https://github.com/advisories/GHSA-h98h-8mxr-m8gx
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-269.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-304.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-253.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2018-001.md
