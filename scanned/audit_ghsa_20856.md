# [C] joblib vulnerable to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-6hrg-qmvc-2xh8
CVE: CVE-2022-21797
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-27
Source: https://github.com/advisories/GHSA-6hrg-qmvc-2xh8
Type: github-advisory

## Affected
- PyPI: `joblib` — affected >=0 <1.2.0

## Details
The package joblib from 0 and before 1.2.0 is vulnerable to Arbitrary Code Execution via the `pre_dispatch` flag in `Parallel()` class due to the `eval()` statement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21797
- https://github.com/joblib/joblib/issues/1128
- https://github.com/joblib/joblib/pull/1321
- https://github.com/joblib/joblib/pull/1327
- https://github.com/joblib/joblib/pull/1352
- https://github.com/joblib/joblib/commit/6638b9e9711ad1ebbf6dd95aa7cee0dca9897b42
- https://github.com/joblib/joblib/commit/b90f10efeb670a2cc877fb88ebb3f2019189e059
- https://security.snyk.io/vuln/SNYK-PYTHON-JOBLIB-3027033
- https://security.gentoo.org/glsa/202401-01
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MJ5XTJS6OKJRRVXWFN5J67K3BYPEOBDF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BVOMMW37OXZWU2EV5ONAAS462IQEHZOF
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MJ5XTJS6OKJRRVXWFN5J67K3BYPEOBDF
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BVOMMW37OXZWU2EV5ONAAS462IQEHZOF
- https://lists.debian.org/debian-lts-announce/2023/03/msg00027.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00020.html
- https://github.com/pypa/advisory-database/tree/main/vulns/joblib/PYSEC-2022-288.yaml
- https://github.com/joblib/joblib
