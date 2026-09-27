# [H] Pallets Project Flask is vulnerable to Denial of Service via Unexpected memory usage

## Summary
Severity: High
Advisory: GHSA-5wv5-4vpf-pj6m
CVE: CVE-2019-1010083
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-07-19
Source: https://github.com/advisories/GHSA-5wv5-4vpf-pj6m
Type: github-advisory

## Affected
- PyPI: `Flask` — affected >=0 <1.0

## Details
The Pallets Project Flask before 1.0 is affected by unexpected memory usage. The impact is denial of service. The attack vector is crafted encoded JSON data. The fixed version is 1. NOTE this may overlap CVE-2018-1000656.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010083
- https://github.com/advisories/GHSA-5wv5-4vpf-pj6m
- https://github.com/pallets/flask
- https://github.com/pypa/advisory-database/tree/main/vulns/flask/PYSEC-2019-179.yaml
- https://www.palletsprojects.com/blog/flask-1-0-released
