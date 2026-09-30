# [C] Keras code injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-x4wf-678h-2pmq
CVE: CVE-2024-3660
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-x4wf-678h-2pmq
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <2.13.1rc0

## Details
A arbitrary code injection vulnerability in TensorFlow's Keras framework (<2.13) allows attackers to execute arbitrary code with the same permissions as the application using a model that allow arbitrary code irrespective of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3660
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/compare/r2.12...r2.13
- https://kb.cert.org/vuls/id/253266
- https://www.kb.cert.org/vuls/id/253266
