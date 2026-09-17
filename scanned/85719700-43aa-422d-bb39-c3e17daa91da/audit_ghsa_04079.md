# [H] Improper Restriction of Operations within the Bounds of a Memory Buffer in Google TensorFlow

## Summary
Severity: High
Advisory: GHSA-q492-f7gr-27rp
CVE: CVE-2018-10055
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2019-04-30
Source: https://github.com/advisories/GHSA-q492-f7gr-27rp
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=1.1.0 <1.7.1
- PyPI: `tensorflow-gpu` — affected >=1.1.0 <1.7.1

## Details
Invalid memory access and/or a heap buffer overflow in the TensorFlow XLA compiler in Google TensorFlow before 1.7.1 could cause a crash or read from other parts of process memory via a crafted configuration file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10055
- https://github.com/tensorflow/tensorflow/commit/c89ab82a82585cdaa90bf4911980e9e845909e78
- https://github.com/advisories/GHSA-q492-f7gr-27rp
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2019-222.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2019-229.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2019-204.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2018-006.md
