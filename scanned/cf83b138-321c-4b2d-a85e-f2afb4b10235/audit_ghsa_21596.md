# [H] Arches vulnerable to execution of arbitrary SQL

## Summary
Severity: High
Advisory: GHSA-gmpq-xrxj-xh8m
CVE: CVE-2022-41892
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2022-11-11
Source: https://github.com/advisories/GHSA-gmpq-xrxj-xh8m
Type: github-advisory

## Affected
- PyPI: `arches` — affected >=0 <6.1.2
- PyPI: `arches` — affected >=6.2.0 <6.2.1
- PyPI: `arches` — affected >=7.0.0 <7.2.0

## Details
### Impact
With a carefully crafted web request, it's possible to execute certain unwanted sql statements against the database.  
Anyone running the impacted versions (<=6.1.1, 6.2.0, >=7.0.0, <=7.1.1) should upgrade as soon as possible.

### Patches
The problem has been patched in the following versions: [6.1.2](https://pypi.org/project/arches/6.1.2/), [6.2.1](https://pypi.org/project/arches/6.2.1/), and [7.2.0](https://pypi.org/project/arches/7.2.0/)
Users are strongly urged to upgrade to the most recent relevant patch.

### Workarounds
There are no workarounds.

### General References 
https://www.w3schools.com/sql/sql_injection.asp
https://en.wikipedia.org/wiki/SQL_injection

### For more information
Post any questions to the [Arches project forum](https://community.archesproject.org/).

## References
- https://github.com/archesproject/arches/security/advisories/GHSA-gmpq-xrxj-xh8m
- https://nvd.nist.gov/vuln/detail/CVE-2022-41892
- https://github.com/archesproject/arches/commit/7ed53e23a616edf3301d95814d9d64de5e3072a9
- https://github.com/archesproject/arches
- https://github.com/pypa/advisory-database/tree/main/vulns/arches/PYSEC-2022-42985.yaml
- https://pypi.org/project/arches/6.1.2
- https://pypi.org/project/arches/7.2.0
- https://securitylab.github.com/advisories/GHSL-2022-070_GHSL-2022-072_Arches
