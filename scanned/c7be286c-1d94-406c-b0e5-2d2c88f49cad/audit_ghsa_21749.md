# [H] Insufficiently Protected Credentials in Apache Superset

## Summary
Severity: High
Advisory: GHSA-hhm3-48h2-597v
CVE: CVE-2021-44451
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-02
Source: https://github.com/advisories/GHSA-hhm3-48h2-597v
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <1.4.0

## Details
Apache Superset up to and including 1.3.2 allowed for registered database connections password leak for authenticated users. This information could be accessed in a non-trivial way. Users should upgrade to Apache Superset 1.4.0 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44451
- https://github.com/advisories/GHSA-hhm3-48h2-597v
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2022-36.yaml
- https://lists.apache.org/thread/xww1pccs2ckb5506wrf1v4lmxg198vkb
