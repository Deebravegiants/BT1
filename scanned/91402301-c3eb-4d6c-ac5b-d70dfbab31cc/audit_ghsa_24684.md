# [M] Deserialization of Untrusted Data in Beaker

## Summary
Severity: Medium
Advisory: GHSA-3cwm-7jmm-774w
CVE: CVE-2013-7489
CWE: CWE-502
Ecosystem: PyPI
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-3cwm-7jmm-774w
Type: github-advisory

## Affected
- PyPI: `Beaker` — affected >=0

## Details
The Beaker library through 1.11.0 for Python is affected by deserialization of untrusted data, which could lead to arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7489
- https://github.com/bbangert/beaker/issues/191
- https://bugzilla.redhat.com/show_bug.cgi?id=1850105
- https://github.com/advisories/GHSA-3cwm-7jmm-774w
- https://github.com/bbangert/beaker
- https://github.com/pypa/advisory-database/tree/main/vulns/beaker/PYSEC-2020-216.yaml
- https://www.openwall.com/lists/oss-security/2020/05/14/11
