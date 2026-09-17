# [H] Improper Input Validation in Google TensorFlow

## Summary
Severity: High
Advisory: GHSA-qx2v-j445-g354
CVE: CVE-2018-7577
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2019-04-30
Source: https://github.com/advisories/GHSA-qx2v-j445-g354
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=1.1.0 <1.7.1
- PyPI: `tensorflow-gpu` — affected >=1.1.0 <1.7.1

## Details
Memcpy parameter overlap in Google Snappy library 1.1.4, as used in Google TensorFlow before 1.7.1, could result in a crash or read from other parts of process memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7577
- https://github.com/tensorflow/tensorflow/commit/dfa9921e6343727b05f42f8d4a918b19528ff994
- https://github.com/advisories/GHSA-qx2v-j445-g354
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2019-225.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2019-232.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2019-207.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2018-005.md
