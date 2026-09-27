# [C] Sony Neural Network Libraries reliance on untrusted inputs prior to v1.0.10

## Summary
Severity: Critical
Advisory: GHSA-4q2w-rw7m-xqw6
CVE: CVE-2019-10844
CWE: CWE-807
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4q2w-rw7m-xqw6
Type: github-advisory

## Affected
- PyPI: `nnabla` — affected >=0 <1.0.10

## Details
nbla/logger.cpp in libnnabla.a in Sony Neural Network Libraries (aka nnabla) prior to v1.0.10 relies on the HOME environment variable, which might be untrusted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10844
- https://github.com/sony/nnabla/issues/209
- https://github.com/sony/nnabla/pull/299
- https://github.com/sony/nnabla/commit/e87347648ab7210529a0e60f0849680de8e9b63a
- https://github.com/advisories/GHSA-4q2w-rw7m-xqw6
- https://github.com/pypa/advisory-database/tree/main/vulns/nnabla/PYSEC-2019-107.yaml
- https://github.com/sony/nnabla
- https://github.com/sony/nnabla/releases/tag/v1.0.10
