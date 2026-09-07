# [H] asyncua Improper Authentication vulnerability

## Summary
Severity: High
Advisory: GHSA-2894-qcqf-g23g
CVE: CVE-2023-26150
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-03
Source: https://github.com/advisories/GHSA-2894-qcqf-g23g
Type: github-advisory

## Affected
- PyPI: `asyncua` — affected >=0 <0.9.96

## Details
Versions of the package asyncua before 0.9.96 are vulnerable to Improper Authentication such that it is possible to access Address Space without encryption and authentication.

**Note:**

This issue is a result of missing checks for services that require an active session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26150
- https://github.com/FreeOpcUa/opcua-asyncio/issues/1014
- https://github.com/FreeOpcUa/opcua-asyncio/pull/1015
- https://github.com/FreeOpcUa/opcua-asyncio/commit/2be7ce80df05de8d6c6ae1ebce6fa2bb7147844a
- https://github.com/FreeOpcUa/opcua-asyncio/commit/b4106dfd5037423c9d1810b48a97296b59cde513
- https://gist.github.com/artfire52/84f7279a4119d6f90381ac49d7121121
- https://github.com/FreeOpcUa/opcua-asyncio
- https://github.com/FreeOpcUa/opcua-asyncio/releases/tag/v0.9.96
- https://github.com/pypa/advisory-database/tree/main/vulns/asyncua/PYSEC-2023-189.yaml
- https://security.snyk.io/vuln/SNYK-PYTHON-ASYNCUA-5673435
