# [M] pymatgen is vulnerable to Regular Expression Denial of Service (ReDoS)

## Summary
Severity: Medium
Advisory: GHSA-5jqp-885w-xj32
CVE: CVE-2022-42964
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-5jqp-885w-xj32
Type: github-advisory

## Affected
- PyPI: `pymatgen` — affected >=0

## Details
An exponential ReDoS (Regular Expression Denial of Service) can be triggered in the pymatgen PyPI package, when an attacker is able to supply arbitrary input to the `GaussianInput.from_string` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42964
- https://github.com/materialsproject/pymatgen/issues/2755
- https://github.com/materialsproject/pymatgen
- https://research.jfrog.com/vulnerabilities/pymatgen-redos-xray-257184
