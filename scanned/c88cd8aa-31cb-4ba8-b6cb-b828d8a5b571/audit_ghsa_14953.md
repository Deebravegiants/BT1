# [M] PyMongo Out-of-bounds Read in the bson module 

## Summary
Severity: Medium
Advisory: GHSA-m87m-mmvp-v9qm
CVE: CVE-2024-5629
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-m87m-mmvp-v9qm
Type: github-advisory

## Affected
- PyPI: `pymongo` — affected >=0 <4.6.3

## Details
Versions of the package pymongo before 4.6.3 are vulnerable to Out-of-bounds Read in the bson module. Using the crafted payload the attacker could force the parser to deserialize unmanaged memory. The parser tries to interpret bytes next to buffer and throws an exception with string. If the following bytes are not printable UTF-8 the parser throws an exception with a single byte.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5629
- https://github.com/mongodb/mongo-python-driver/commit/56b6b6dbc267d365d97c037082369dabf37405d2
- https://gist.github.com/keltecc/62a7c2bf74a997d0a7b48a0ff3853a03
- https://github.com/mongodb/mongo-python-driver
- https://jira.mongodb.org/browse/PYTHON-4305
- https://lists.debian.org/debian-lts-announce/2024/06/msg00007.html
- https://security.snyk.io/vuln/SNYK-PYTHON-PYMONGO-6370597
