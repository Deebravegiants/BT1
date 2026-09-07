# [M] cleo is vulnerable to Regular Expression Denial of Service (ReDoS)

## Summary
Severity: Medium
Advisory: GHSA-2p9h-ccw7-33gf
CVE: CVE-2022-42966
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-2p9h-ccw7-33gf
Type: github-advisory

## Affected
- PyPI: `cleo` — affected >=1.0.0a1 <2.0.0

## Details
An exponential ReDoS (Regular Expression Denial of Service) can be triggered in the cleo PyPI package, when an attacker is able to supply arbitrary input to the Table.set_rows method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42966
- https://github.com/python-poetry/cleo/pull/285
- https://github.com/python-poetry/cleo/commit/b5b9a04d2caf58bf7cf94eb7ae4a1ebbe60ea455
- https://github.com/advisories/GHSA-2p9h-ccw7-33gf
- https://github.com/pypa/advisory-database/tree/main/vulns/cleo/PYSEC-2022-43178.yaml
- https://github.com/python-poetry/cleo
- https://github.com/python-poetry/cleo/releases/tag/2.0.0
- https://research.jfrog.com/vulnerabilities/cleo-redos-xray-257186
