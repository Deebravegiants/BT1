# [C] scikit-learn Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-jjw5-xxj6-pcv5
CVE: CVE-2020-13092
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jjw5-xxj6-pcv5
Type: github-advisory

## Affected
- PyPI: `scikit-learn` — affected >=0

## Details
scikit-learn (aka sklearn) through 0.23.0 can unserialize and execute commands from an untrusted file that is passed to the `joblib.load()` function, if `__reduce__` makes an `os.system call`.
NOTE: third parties dispute this issue because the joblib.load() function is documented as unsafe and it is the user's responsibility to use the function in a secure manner.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13092
- https://github.com/0FuzzingQ/vuln/blob/master/sklearn%20unserialize.md
- https://github.com/pypa/advisory-database/tree/main/vulns/scikit-learn/PYSEC-2020-107.yaml
- https://github.com/scikit-learn/scikit-learn
- https://scikit-learn.org/stable/modules/model_persistence.html#security-maintainability-limitations
