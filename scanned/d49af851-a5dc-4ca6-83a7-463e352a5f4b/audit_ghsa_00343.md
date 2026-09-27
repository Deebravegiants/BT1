# [M] In marshmallow library the schema "only" option treats an empty list as implying no "only" option

## Summary
Severity: Medium
Advisory: GHSA-9q2p-fj49-vpxj
CVE: CVE-2018-17175
CWE: CWE-358
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-9q2p-fj49-vpxj
Type: github-advisory

## Affected
- PyPI: `marshmallow` — affected >=0 <2.15.1
- PyPI: `marshmallow` — affected >=3.0a0 <3.0.0b9

## Details
In the marshmallow library before 2.15.1 and 3.x before 3.0.0b9 for Python, the schema "only" option treats an empty list as implying no "only" option, which allows a request that was intended to expose no fields to instead expose all fields (if the schema is being filtered dynamically using the "only" option, and there is a user role that produces an empty value for "only").

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17175
- https://github.com/marshmallow-code/marshmallow/issues/772
- https://github.com/marshmallow-code/marshmallow/pull/777
- https://github.com/marshmallow-code/marshmallow/pull/782
- https://github.com/marshmallow-code
- https://github.com/pypa/advisory-database/tree/main/vulns/marshmallow/PYSEC-2018-67.yaml
