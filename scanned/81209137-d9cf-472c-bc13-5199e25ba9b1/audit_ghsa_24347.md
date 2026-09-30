# [C] Argument injection in python-libnmap

## Summary
Severity: Critical
Advisory: GHSA-qwqv-j7jr-4hp6
CVE: CVE-2022-30284
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-06
Source: https://github.com/advisories/GHSA-qwqv-j7jr-4hp6
Type: github-advisory

## Affected
- PyPI: `python-libnmap` — affected >=0 <0.7.3

## Details
In the python-libnmap package through 0.7.2 for Python, remote command execution can occur (if used in a client application that does not validate arguments).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30284
- https://github.com/savon-noir/python-libnmap/commit/c36fecde90017befeb4853396d0e2aac93c95b64
- https://github.com/pypa/advisory-database/tree/main/vulns/python-libnmap/PYSEC-2022-42999.yaml
- https://github.com/savon-noir/python-libnmap
- https://github.com/savon-noir/python-libnmap/releases
- https://github.com/savon-noir/python-libnmap/releases/tag/v0.7.3
- https://libnmap.readthedocs.io/en/latest/process.html#using-libnmap-process
- https://pypi.org/project/python-libnmap
- https://www.swascan.com/security-advisory-libnmap-2
