# [H] Null pointer dereference in TensorFlow leads to exploitation

## Summary
Severity: High
Advisory: GHSA-jfq2-rj7f-9gvf
CVE: CVE-2018-7576
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-04-24
Source: https://github.com/advisories/GHSA-jfq2-rj7f-9gvf
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=1.0.0 <1.6.0
- PyPI: `tensorflow-gpu` — affected >=1.0.0 <1.6.0

## Details
Google TensorFlow 1.0.0 through 1.5.1 is affected by: Null Pointer Dereference. The type of exploitation is: context-dependent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7576
- https://github.com/tensorflow/tensorflow/commit/c48431588e7cf8aff61d4c299231e3e925144df8
- https://github.com/advisories/GHSA-jfq2-rj7f-9gvf
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2019-224.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2019-231.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2019-206.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2018-002.md
