# [H] asyncua vulnerable to denial of service via infinite loop

## Summary
Severity: High
Advisory: GHSA-gfvq-mxw3-mfq3
CVE: CVE-2023-26151
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-03
Source: https://github.com/advisories/GHSA-gfvq-mxw3-mfq3
Type: github-advisory

## Affected
- PyPI: `asyncua` — affected >=0 <0.9.96

## Details
Versions of the package asyncua before 0.9.96 are vulnerable to Denial of Service (DoS) such that an attacker can send a malformed packet and as a result, the server will enter into an infinite loop and consume excessive memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26151
- https://github.com/FreeOpcUa/opcua-asyncio/issues/1013
- https://github.com/FreeOpcUa/opcua-asyncio/pull/1039
- https://github.com/FreeOpcUa/opcua-asyncio/commit/f6603daa34a93a658f0e176cb0b9ee5a6643b262
- https://gist.github.com/artfire52/1540b234350795e0ecb4d672608dbec8
- https://github.com/FreeOpcUa/opcua-asyncio
- https://github.com/FreeOpcUa/opcua-asyncio/releases/tag/v0.9.96
- https://github.com/pypa/advisory-database/tree/main/vulns/asyncua/PYSEC-2023-190.yaml
- https://security.snyk.io/vuln/SNYK-PYTHON-ASYNCUA-5673709
